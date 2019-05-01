% raspberry pi files

classdef raspi < matlabshared.internal.LinuxSystemInterface & ...
        raspi.internal.PWMBase & matlab.mixin.CustomDisplay & ...
        matlab.I2C.Master & matlab.SPI.Master
    %RASPI Access Raspberry Pi hardware peripherals.
    %
    % obj = RASPI(DEVICEADDRESS, USERNAME, PASSWORD) creates a RASPI object
    % connected to the Raspberry Pi hardware at DEVICEADDRESS with login
    % credentials USERNAME and PASSWORD. The DEVICEADDRESS can be an 
    % IP address such as '192.168.0.10' or a hostname such as
    % 'raspberrypi-MJONES.foo.com'. 
    %
    % obj = RASPI creates a RASPI object connected to Raspberry Pi hardware
    % using saved values for DEVICEADDRESS, USERNAME and PASSWORD.
    % 
    % Type <a href="matlab:methods('raspi')">methods('raspi')</a> for a list of methods of the raspi object.
    %
    % Type <a href="matlab:properties('raspi')">properties('raspi')</a> for a list of properties of the raspi object.
    
    % Copyright 2013-2016 The MathWorks, Inc.
    
    properties (Dependent)
        DeviceAddress
        Port
    end
    
    properties (SetAccess = private)
        BoardName
        AvailableLEDs
        AvailableDigitalPins
        AvailableSPIChannels
        AvailableI2CBuses
        I2CBusSpeed
        AvailableWebcams = {} 
    end
    
    properties (Access = private)
        IpNode
        Credentials
        Sequence = 0
        Version
    end
    
    properties (Hidden)
        Ssh
    end
    
    properties (Access = private)
        Tcp
        BoardInfo
        DigitalPin
        LED
        I2C
        SPI
        
        % Maintain a map of created objects to gain exclusive access
        ConnectionMap = containers.Map
        Initialized = false
    end
    
    properties (Hidden)
        WebcamInfo
    end
    
    properties (Hidden, Constant)
        REQ_HEADER_SIZE            = 3
        REQ_HEADER_PRECISION       = 'uint32'
        REQ_MAX_PAYLOAD_SIZE       = 1024
        RESP_HEADER_SIZE           = 3
        RESP_HEADER_PRECISION      = 'uint32'
        RESP_MAX_PAYLOAD_SIZE      = (2000*1080*3)/2
        
        % Reserved
        REQUEST_ECHO               = 0
        REQUEST_VERSION            = 1
        REQUEST_AUTHORIZATION      = 2
        
        % LED requests
        REQUEST_LED_GET_TRIGGER    = 1000
        REQUEST_LED_SET_TRIGGER    = 1001
        REQUEST_LED_WRITE          = 1002
        
        % GPIO requests
        REQUEST_GPIO_INIT          = 2000
        REQUEST_GPIO_TERMINATE     = 2001
        REQUEST_GPIO_READ          = 2002
        REQUEST_GPIO_WRITE         = 2003
        REQUEST_GPIO_GET_DIRECTION = 2004

        % System requests
        REQUEST_I2C_BUS_AVAILABLE  = 3000
        
        % Constant used for storing board parameters
        BoardPref = 'Raspberry Pi';
    end
    
    properties (Constant, Access = private)
        % I2C requests
        REQUEST_I2C_INIT           = 3001
        REQUEST_I2C_READ           = 3002
        REQUEST_I2C_WRITE          = 3003
        REQUEST_I2C_TERMINATE      = 3004
        REQUEST_I2C_READ_REGISTER  = 3005
        REQUEST_I2C_WRITE_REGISTER = 3006
        
        MAX_I2C_ADDRESS = hex2dec('7f')
        
        AvailablePrecisions = {'int8','uint8','int16','uint16',...
            'int32','uint32','int64','uint64'}
        SIZEOF = struct(...
            'int8',1, ...
            'uint8',1, ...
            'int16',2, ...
            'uint16',2, ...
            'int32',4, ...
            'uint32',4, ...
            'int64',8, ...
            'uint64',8, ...
            'single',4, ...
            'double',8)
    end
    
    properties (Hidden, Constant)
        EXPECTED_SERVER_VERSION = uint32([16, 2, 0])
        AVAILABLE_LED_TRIGGERS  = {'none', 'mmc0'}
        GPIO_INPUT              = 0
        GPIO_OUTPUT             = 1
        NUMDIGITALPINS          = 32
        UPINMODESTR             = {'unset','DigitalInput','DigitalOutput','PWM','Servo'}
        PINMODE_UNSET           = 1
        PINMODE_DI              = 2
        PINMODE_DO              = 3
        PINMODE_PWM             = 4
        PINMODE_SERVO           = 5
        VDD                     = 3.3
% The frequencies (Hz) for each sample rate in PIGPIO  are:                   
% 1us: 40000 20000 10000 8000 5000 4000 2500 2000 1600
%      1250  1000   800  500  400  250  200  100   50
% 2us: 20000 10000  5000 4000 2500 2000 1250 1000  800
%      625   500   400  250  200  125  100   50   25 
% 4us: 10000  5000  2500 2000 1250 1000  625  500  400
%      313   250   200  125  100   63   50   25   13
% 5us: 8000  4000  2000 1600 1000  800  500  400  320
%      250   200   160  100   80   50   40   20   10
% 8us: 5000  2500  1250 1000  625  500  313  250  200
%      156   125   100   63   50   31   25   13    6
% 10us:4000  2000  1000  800  500  400  250  200  160
%      125   100    80   50   40   25   20   10    5
% We use 5us sample rate for minimum CPU load.
        AVAILABLE_PWM_FREQUENCY = [8000,4000,2000,1600,1000,800,500,400,320,...
            250,200,160,100,80,50,40,20,10]
    end
    
    methods (Hidden)
        function obj = raspi(hostname, username, password, port)
            % Create a connection to Raspberry Pi hardware.
            narginchk(0,4);
            
            % Register the error message catalog location
            [~] = registerrealtimecataloglocation(raspi.internal.getRaspiBaseRoot);
            
            hb = raspi.internal.BoardParameters(obj.BoardPref);
            if nargin < 1
                hostname = hb.getParam('hostname');
                if isempty(hostname)
                    error(message('raspi:utils:InvalidDeviceAddress'));
                end
            end
            if nargin < 2
                username = hb.getParam('username');
                if isempty(username)
                    error(message('raspi:utils:InvalidUsername'));
                end
            end
            if nargin < 3
                password = hb.getParam('password'); 
                if isempty(password)
                    error(message('raspi:utils:InvalidPassword'));
                end
            end
            if nargin < 4
                port = raspi.internal.getServerPort;
            end
            
            % Validate and store device address
            try
                obj.IpNode = matlabshared.internal.ipnode(hostname, port);
                obj.Credentials = matlabshared.internal.credentials(username, password);
            catch ME
                throwAsCaller(ME);
            end
            
            % Check if there is an existing connection
            if isKey(obj.ConnectionMap, obj.IpNode.Hostname)
                error(message('raspi:utils:ConnectionExists', obj.IpNode.Hostname));
            end
            
            % Create an SSH client
            [~,hashKey] = fileparts(tempname);
            if ~isequal(obj.IpNode.Hostname,'localhost')
                obj.Ssh = matlabshared.internal.ssh2client(obj.IpNode.Hostname, ...
                    obj.Credentials.Username, obj.Credentials.Password);
                if ~isServerRunning(obj)
                    launchServer(obj);
                    ts = tic;
                    while (toc(ts) < 5) && ~isServerRunning(obj)
                        pause(0.1);
                    end
                    if ~isServerRunning(obj)
                        error(message('raspi:utils:UnableToConnect',obj.DeviceAddress));
                    end
                end
                execute(obj.Ssh, ['echo `pgrep ' raspi.internal.getServerName '` | sudo tee /tmp/.' hashKey]);
            end
            
            % Create TCP client
            obj.Tcp = matlabshared.network.internal.TCPClient(...
                obj.IpNode.Hostname, obj.IpNode.Port);
            try
                connect(obj.Tcp);
            catch ME
                baseME = MException(message('raspi:utils:TCPConnectionError', obj.IpNode.Hostname));
                EX = addCause(baseME, ME);
                throw(EX);
            end
            
            % Authorize user 
            try
                authorize(obj,hashKey);
            catch ME
                error(message('raspi:utils:NotAuthorized', obj.DeviceAddress));
            end
            
            % Get and set server version. Note that the set method for
            % Version checks that we are compatible with the server.
            obj.Version = getServerVersion(obj);
            
            % Set board revision and static board information
            obj.BoardName = getBoardName(obj);
            hInfo = raspi.internal.BoardInfo(obj.BoardName);
            if isempty(hInfo.Board)
                error(message('raspi:utils:UnknownBoardRevision'));
            end
            obj.BoardInfo = hInfo.Board;
            
            % Tally all supported peripherals available on board
            getAvailablePeripherals(obj);
            
            % Add current connection to connectionMap
            obj.ConnectionMap(obj.IpNode.Hostname) = 0;
            obj.Initialized = true;
            
            % New code for I2C master
            obj.AvailableI2CSpeeds = 100e3;
            obj.I2CSpeed = 100e3;
            
            % Store board parameters for a future session
            hb = raspi.internal.BoardParameters(obj.BoardPref);
            hb.setParam('hostname', obj.DeviceAddress);
            hb.setParam('username', obj.Credentials.Username);
            hb.setParam('password', obj.Credentials.Password);
        end
    end
    
    methods(Access = private, Static)
        function name = matlabCodegenRedirect(~)
            name = 'raspi.codegen.raspi';
        end
    end
    
    methods (Access = protected)
        function ret = getAvailableI2CBusNumbers(obj) %#ok<MANU>
            ret = 1;
        end

        function ret = getAvailableSPIChipSelect(obj) %#ok<MANU>
            ret = [0,1];
        end
    end
    
    % GET / SET methods
    methods
        function value = get.DeviceAddress(obj)
            value = obj.IpNode.Hostname;
        end
        
        function value = get.Port(obj)
            value = obj.IpNode.Port;
        end
        
        function set.Version(obj,val)
            if ~isequal(val,raspi.internal.getServerVersion)
                error(message('raspi:utils:UnexpectedServerVersion'));
            end
            obj.Version = val;
        end
    end
    
    methods
        function openShell(obj)
            % openShell(rpi) opens an interactive command shell to
            % Raspberry Pi hardware.
            openShell(obj.Ssh);
        end
        
        function ret = scanI2CBus(obj, bus)
            % scanI2CBus(rpi, bus) returns a list of addresses
            % corresponding to devices discovered on the I2C bus.
            %
            % scanI2CBus(rpi) is supported if there is a single available I2C bus.
            
            if nargin < 2
                buses = obj.AvailableI2CBuses;
                if isempty(buses)
                    bus = '';
                else
                    bus = buses{1};
                end
            end
            validateattributes(bus, {'char'}, ...
                {'row','nonempty'}, '', 'bus');
            if ~any(strcmpi(bus, obj.AvailableI2CBuses))
                error(message('raspi:utils:InvalidI2CBus',bus));
            end
            
            id = getId(bus);
            busNumber = obj.I2C.(id).Number;
            output = execute(obj.Ssh,['sudo i2cdetect -y ', int2str(busNumber)]);
            output = regexprep(output, '\d\d:', '');
            ret = regexp(output, '[abcdefABCDEF0-9]{2,2}', 'match');
            for i = 1:numel(ret)
                ret{i} = ['0x' upper(ret{i})];
            end
        end
        
        function enableSPI(obj)
            % enableSPI(rpi) enables SPI peripheral on the Raspberry Pi
            % hardware.
            
            try
                % SPIDEV module name changed from spi_bcm2708 to spi_bcm2835 at
                % some point.
                execute(obj.Ssh,'sudo modprobe spidev');
                execute(obj.Ssh,'sudo modprobe spi_bcm2708 || sudo modprobe spi_bcm2835');
            catch ME
                baseME = MException(message('raspi:utils:CannotEnableSPI'));
                EX = addCause(baseME,ME);
                throw(EX);
            end
            getAvailablePeripherals(obj);
        end
        
        function disableSPI(obj)
            % disableSPI(rpi) disables SPI peripheral on the Raspberry Pi
            % hardware.
            try
                execute(obj.Ssh,'sudo rmmod spi_bcm2835 || sudo rmmod spi_bcm2708');
                pause(1);
                output = execute(obj.Ssh,'cat /proc/modules');         
            catch ME
                baseME = MException(message('raspi:utils:CannotEnableSPI'));
                EX = addCause(baseME, ME);
                throw(EX);
            end
            if ~isempty(regexp(output, 'spi_bcm2708', 'match'))
                error(message('raspi:utils:CannotDisableSPI'));
            end
            getAvailablePeripherals(obj);
        end
        
        function enableI2C(obj, speed)
            % enableI2C(rpi) enables I2C peripheral on the Raspberry Pi
            % hardware.
            if nargin < 2
                speed = 100000;
            else
                validateattributes(speed, {'numeric'}, ...
                    {'scalar','nonzero','nonnan'}, '', 'speed');
            end
            try
                execute(obj.Ssh,'sudo modprobe i2c_dev');
                execute(obj.Ssh,sprintf('sudo modprobe i2c_bcm2708 baudrate=%d', speed));
                pause(1);
                output = execute(obj.Ssh,'cat /proc/modules');
            catch ME
                baseME = MException(message('raspi:utils:CannotEnableI2C'));
                EX = addCause(baseME, ME);
                throw(EX);
            end
            if isempty(regexp(output, 'i2c_bcm2708', 'match'))
                error(message('raspi:utils:CannotEnableI2C'));
            end
            getAvailablePeripherals(obj);
        end
        
        function disableI2C(obj)
            % disableI2C(rpi) disables I2C peripheral on the Raspberry Pi
            % hardware.
            try
                execute(obj.Ssh,'sudo modprobe -r i2c_dev');
                execute(obj.Ssh,'sudo modprobe -r i2c_bcm2708');
                pause(1);
                output = execute(obj.Ssh,'cat /proc/modules');
            catch ME
                baseME = MException(message('raspi:utils:CannotDisableI2C'));
                EX = addCause(baseME, ME);
                throw(EX);
            end
            if ~isempty(regexp(output, 'i2c_bcm2708', 'match'))
                error(message('raspi:utils:CannotDisableI2C'));
            end
            getAvailablePeripherals(obj);
        end
        
        function showPins(obj)
            % showPins(rpi) shows a diagram of user accessible pins.
            showImage(obj.BoardInfo.GPIOImgFile, ...
                [obj.BoardName ': Pin Map']);
        end
        
        % LED interface
        function showLEDs(obj)
            % showLEDs(rpi) shows locations of user accessible LED's.
            showImage(obj.BoardInfo.LEDImgFile, ...
                [obj.BoardName ': LED Locations']);
        end
        
        function writeLED(obj, led, value)
            % writeLED(rpi, led, value) sets the led state to the given value.
            led = validatestring(led, obj.AvailableLEDs);
            validateattributes(value, {'numeric', 'logical'}, ...
                {'scalar'}, '', 'value');
            if isnumeric(value) && ~((value == 0) || (value == 1))
                error(message('raspi:utils:InvalidLEDValue'));
            end
            id = getId(led);
            if ~isequal(obj.LED.(id).Trigger, 'none')
                configureLED(obj, led, 'none');
            end
            
            % Send an LED write request
            sendRequest(obj,obj.REQUEST_LED_WRITE, ...
                uint32(obj.LED.(id).Number), logical(value));
            recvResponse(obj);
        end
        
        % GPIO interface
        function pinMode = configureDigitalPin(obj, pinNumber, pinMode)
            % configureDigitalPin(rpi, pinNumber, pinMode)
            warning(message('raspi:utils:DeprecateConfigureDigitalPin'));
            if nargin == 2
                pinMode = configurePin(obj,pinNumber);
            elseif nargin == 3
                pinMode = validatestring(pinMode, {'input','output'});
                switch pinMode
                    case {'input'}
                        pinMode = configurePin(obj,pinNumber,'DigitalInput');
                    case {'output'}
                        pinMode = configurePin(obj,pinNumber,'DigitalOutput');
                end
            end
        end
        
        function pinMode = configurePin(obj,pinNumber,pinMode,varargin)
            % configurePin(rpi,pinNumber,pinMode,varargin)
            checkDigitalPin(obj,pinNumber);
            if nargin == 2
                % Return current pin configuration
                pinName = getPinName(pinNumber);
                pinMode = obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode};
            elseif nargin == 3
                % Configure pin for desired mode. First unset the pin if it
                % was being used previously for a different mode
                pinMode = validatestring(pinMode,obj.UPINMODESTR(1:obj.PINMODE_PWM));
                configurePinUnset(obj,pinNumber);
                switch pinMode
                    case obj.UPINMODESTR{obj.PINMODE_DI}
                        configurePinDigi(obj,pinNumber,obj.PINMODE_DI);
                    case obj.UPINMODESTR{obj.PINMODE_DO}
                        configurePinDigi(obj,pinNumber,obj.PINMODE_DO);
                    case obj.UPINMODESTR{obj.PINMODE_PWM}
                        if nargin < 4
                            frequency = 500; % Hz
                        else
                            frequency = varargin{1};
                            validateattributes(frequency,{'numeric'},...
                                {'scalar','nonnegative'},'','frequency');
                        end
                        configurePinPWM(obj,pinNumber,frequency);
                    case obj.UPINMODESTR{obj.PINMODE_UNSET}
                        % Already unset at the top of the switch
                        % nothing to do here
                end
            end
        end
        
        function pinMode = getDigitalPinConfiguration(obj, pinNumber)
            % pinMode = getDigitalPinConfiguration(rpi, pinNumber) returns
            % the current configuration of the specified digital pin.
            checkDigitalPin(obj, pinNumber);
            pinName = getPinName(pinNumber);
            pinMode = obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode};
        end
        
        function value = readDigitalPin(obj, pinNumber)
            % value = readDigitalPin(rpi, pinNumber) reads the logical
            % state of the specified digital pin.
            checkDigitalPin(obj, pinNumber);
            pinName = getPinName(pinNumber);
            if ~obj.DigitalPin.(pinName).Inuse
                configurePin(obj, pinNumber, 'DigitalInput');
            end
            if obj.DigitalPin.(pinName).Mode ~= obj.PINMODE_DI
                error(message('raspi:utils:InvalidDigitalRead',pinNumber,...
                    obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode+1}));
            end
            
            % Send read request
            sendRequest(obj,obj.REQUEST_GPIO_READ, uint32(pinNumber));
            value = logical(recvResponse(obj));
        end
        
        function writePWMVoltage(obj,pin,voltage)
            % writePWMVoltage - Set PWM pin voltage
            %   writePWMVoltage(obj,pin,voltage)
            %
            %   Inputs:
            %       pin     - pin number, e.g. 4
            %       voltage - 0 - 3.3
            %
            %   Example:
            %       r = raspi;
            %       writePWMVoltage(r,4,2.5)
            
            validateattributes(voltage,{'numeric'},...
                {'scalar' '>=' 0 '<=' obj.VDD}, '', 'voltage');
            obj.writePWMDutyCycle(pin,voltage/obj.VDD);
        end
        
        function writePWMFrequency(obj,pinNumber,frequency)
            % writePWMFrequency - Set PWM pin frequency
            %   writePWMFrequency(obj,pin,frequency)
            %
            %   Inputs:
            %       pin   - pin number, e.g. 4
            %       frequency - 1 - 1000000000
            %
            %   Example:
            %       writePWMFrequency(bbb, 'P8_13', 2000000)
            
            validateattributes(frequency,{'numeric'},...
                {'scalar','positive','real','finite'}, '', 'frequency');
            if ~ismember(frequency,obj.AVAILABLE_PWM_FREQUENCY)
                error(message('raspi:utils:InvalidPWMFrequency',...
                    sprintf('%d, ',obj.AVAILABLE_PWM_FREQUENCY)));
            end
            
            % Enable PWM output if required
            checkDigitalPin(obj,pinNumber);
            pinName = getPinName(pinNumber);
            if ~obj.DigitalPin.(pinName).Inuse
                configurePin(obj,pinNumber,'PWM');
            end
            if obj.DigitalPin.(pinName).Mode ~= obj.PINMODE_PWM
                error(message('raspi:utils:InvalidPWMWrite',pinNumber,...
                    obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode+1}));
            end
            setPWMFrequency(obj,pinNumber,frequency);
        end
        
        function writePWMDutyCycle(obj,pinNumber,dutyCycle)
            %   Output a PWM signal on a digital pin.
            %
            %   Syntax:
            %   writePWMDutyCycle(r,pin,dutyCycle)
            %
            %   Description:
            %   Set the specified duty cycle on the specified digital pin.
            %
            %   Example:
            %   Set the bightness of the LED on digital pin 4 of the Raspberry Pi hardware to 33%
            %       r = raspi();
            %       writePWMDutyCycle(r,4,0.33);
            %
            %   Input Arguments:
            %   r         - Raspberry Pi hardware
            %   pin       - Digital pin number
            %   dutyCycle - PWM signal duty cycle between 0 and 1.
            %
            %   See also writeDigitalPin, writePWMVoltage
            % Send write request
            checkDigitalPin(obj,pinNumber);
            pinName = getPinName(pinNumber);
            if ~obj.DigitalPin.(pinName).Inuse
                configurePin(obj,pinNumber,'PWM');
            end
            if obj.DigitalPin.(pinName).Mode ~= obj.PINMODE_PWM
                 error(message('raspi:utils:InvalidPWMWrite',pinNumber,...
                    obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode+1}));
            end
            setPWMDutyCycle(obj,pinNumber,dutyCycle);
        end
        
        function writeDigitalPin(obj, pinNumber, value)
            % writeDigitalPin(rpi, pinNumber, value) sets the state of a
            % digital pin to the given value.
            checkDigitalPin(obj,pinNumber);
            checkDigitalValue(value);
            pinName = getPinName(pinNumber);
            if ~obj.DigitalPin.(pinName).Inuse
                configurePin(obj, pinNumber, 'DigitalOutput');
            end
            if obj.DigitalPin.(pinName).Mode ~= obj.PINMODE_DO
                error(message('raspi:utils:InvalidDigitalWrite',pinNumber,...
                    obj.UPINMODESTR{obj.DigitalPin.(pinName).Mode+1}));
            end
            
            % Send write request
            sendRequest(obj,obj.REQUEST_GPIO_WRITE, uint32(pinNumber), ...
                logical(value));
            recvResponse(obj);
        end
        
        % I2C interface
        function i2cObj = i2cdev(obj,varargin)
            i2cObj = raspi.internal.i2cdev(obj,varargin{:});
        end
        
        % SPI interface
        function spiObj = spidev(obj,varargin)
            spiObj = raspi.internal.spidev(obj,varargin{:});
        end
        
        % Serial interface
        function serialObj = serialdev(obj,varargin)
            serialObj = raspi.internal.serialdev(obj,varargin{:});
        end
        
        % CameraBoard interface
        function camObj = cameraboard(obj, varargin)
            camObj = raspi.internal.cameraboard(obj,varargin{:});
        end
        
        function servoObj = servo(obj,varargin)
            servoObj = raspi.internal.servo(obj,varargin{:});
        end
        
        function webcamObj = webcam(obj,varargin)
            % webcam - Create a web camera object
            %   webcamObj = webcam(obj, resolution)
            %
            %   Inputs:
            %       resolution - Camera resolution. Defaults to '320x240'
            %
            %   Output:
            %       webcamObj  - Web camera object
            %
            %   Example:
            %       webcamObj = webcam(bbb, '320x240')
            
            webcamObj = raspi.internal.webcam(obj,varargin{:});
        end
        
        function s = sensehat(obj,varargin)
            % sensehat - Create a Sense HAT object
            %
            s = raspi.internal.sensehat(obj,varargin{:});
        end
    end
    
    methods (Hidden)
        function sendRequest(obj, requestId, varargin)
            %sendRequest Send request to hardware.
            obj.Sequence = obj.Sequence + 1;
            req = createRequest(obj, requestId, varargin{:});
            send(obj.Tcp, req);
        end
        
        function [data,err] = recvResponse(obj)
            %recvResponse Return response from hardware.
            %   [DATA,ERR] = recvResponse(obj) returns DATA error status
            %   ERR from hardware.
            
            data = [];
            resp = [];
            while isempty(resp) || resp(2) ~= obj.Sequence
                resp = receive(obj.Tcp, ...
                    obj.RESP_HEADER_SIZE, ...
                    obj.RESP_HEADER_PRECISION);
                if resp(1) == 0
                    data = receive(obj.Tcp,resp(3),'uint8');
                end
            end
            % We have desired sequence #
            err = resp(1);
            if err ~= 0 && nargout < 2
                throw(getServerException(err))
            end
        end
        
        function config = getAvailableLEDConfigurations(obj, led)
            % config = getAvailableLEDConfigurations(obj, led) returns
            % available LED configurations.
            led = validatestring(led, obj.AvailableLEDs);
            id = getId(led);
            sendRequest(obj,obj.REQUEST_LED_GET_TRIGGER, ...
                uint32(obj.LED.(id).Number));
            payload = strtrim(char(recvResponse(obj)));
            payload = regexprep(payload, '\[|\]', '');
            config = regexp(payload, '\s+', 'split');
        end
        
        function trigger = getLEDConfiguration(obj, led)
            % trigger = getLEDConfiguration(obj, led) returns current LED
            % configuration.
            led = validatestring(led, obj.AvailableLEDs);
            id = getId(led);
            sendRequest(obj,obj.REQUEST_LED_GET_TRIGGER, ...
                uint32(obj.LED.(id).Number));
            payload = recvResponse(obj);
            ret     = regexp(char(payload), '\[(.+)]', 'tokens', 'once');
            trigger = ret{1};
        end
        
        function configureLED(obj, led, trigger)
            %configureLED(obj, led, trigger) configures LED trigger.
            led = validatestring(led, obj.AvailableLEDs);
            id = getId(led);
            trigger = validatestring(trigger, ...
                obj.LED.(id).AvailableTriggers, '', 'trigger');
            
            % Send a set request for LED trigger
            sendRequest(obj,obj.REQUEST_LED_SET_TRIGGER, ...
                uint32(obj.LED.(id).Number), trigger);
            recvResponse(obj);
            
            % Change trigger state
            obj.LED.(id).Trigger = trigger;
        end
    end
    
    methods (Hidden, Access = public)
        function result = isV4l2Installed(obj)
            try
                execute(obj.Ssh,'v4l2-ctl');
                result = true;
            catch
                result = false;
            end
        end
        
        function result = hasInternetAccess(obj)
            try
                execute(obj.Ssh,'ping -c 2 www.google.com');
                result = true;
            catch
                result = false;
            end
        end
        
        function installV4l2(obj)
            try
                disp('First time use setup ...');
                execute(obj.Ssh,'sudo apt-get install v4l-utils');
            catch
                error(message('raspi:utils:v4l2InstallFailed'));
            end
        end
    end
    
    methods (Access = protected)
        function ret = isServerRunning(obj)
            cmd = ['pgrep ' raspi.internal.getServerName];
            [~,~,status] = execute(obj.Ssh,cmd,false);
            ret = status == 0;  
        end
        
        function ret = isServerAvailable(obj)
            cmd = ['stat ' raspi.internal.getServerDir '/' raspi.internal.getServerName];
            [~,~,status] = execute(obj.Ssh,cmd,false);
            ret = status == 0;  
        end
        
        function startServerApp(obj)
            % Kill running server. Do not throw exception when executing
            % this command.
            serverExe = [raspi.internal.getServerDir '/' raspi.internal.getServerName];
            cmd = ['sudo ' serverExe ' ' num2str(raspi.internal.getServerPort) ' &> /dev/null &'];
            execute(obj.Ssh,cmd);
        end
        
        function launchServer(obj)
            if ~isServerAvailable(obj)
                % raspi.updateServer also starts the server
                raspi.updateServer(obj.DeviceAddress,...
                    obj.Credentials.Username,...
                    obj.Credentials.Password);
            else
                startServerApp(obj);
            end
        end
        
        function configurePinDigi(obj,pinNumber,pinModeEnum)
            if pinModeEnum == obj.PINMODE_DI
                direction = 0;
            else
                direction = 1;
            end
            sendRequest(obj, ...
                obj.REQUEST_GPIO_INIT, ...
                uint32(pinNumber), ...
                uint8(direction));
            recvResponse(obj);
            pinName = getPinName(pinNumber);
            obj.DigitalPin.(pinName).Inuse = true;
            obj.DigitalPin.(pinName).Mode  = pinModeEnum;
        end
        
        function configurePinPWM(obj,pinNumber,frequency)
            initPWM(obj,pinNumber,frequency,0);
            pinName = getPinName(pinNumber);
            obj.DigitalPin.(pinName).Inuse = true;
            obj.DigitalPin.(pinName).Mode  = obj.PINMODE_PWM;
        end
        
        function configurePinUnset(obj,pinNumber)
            % pinMode == unset
            pinName = getPinName(pinNumber);
            if ~obj.DigitalPin.(pinName).Inuse
                return;
            end
            switch obj.DigitalPin.(pinName).Mode
                case {obj.PINMODE_DI,obj.PINMODE_DO}
                    % Digital I/O (GPIO)
                    sendRequest(obj,...
                        obj.REQUEST_GPIO_TERMINATE,...
                        uint32(pinNumber));
                    recvResponse(obj);
                case obj.PINMODE_PWM
                    % PWM
                    terminatePWM(obj,pinNumber);
            end
            obj.DigitalPin.(pinName).Inuse = false;
            obj.DigitalPin.(pinName).Mode  = obj.PINMODE_UNSET;
        end
        
        function displayScalarObject(obj)
            header = getHeader(obj);
            disp(header);
            % Display main options
            fprintf('         DeviceAddress: %-30s\n',obj.DeviceAddress);
            fprintf('                  Port: %-30d\n',obj.Port);
            fprintf('             BoardName: %-30s\n',obj.BoardName);
            fprintf('         AvailableLEDs: %-30s\n',...
                i_printStrCell(obj.AvailableLEDs));  
            fprintf('  AvailableDigitalPins: %-30s\n',...
                i_printArray(obj.AvailableDigitalPins));
            fprintf('  AvailableSPIChannels: %-30s\n',...
                i_printStrCell(obj.AvailableSPIChannels));
            fprintf('     AvailableI2CBuses: %-30s\n',...
                i_printStrCell(obj.AvailableI2CBuses));
            fprintf('      AvailableWebcams: %-30s\n',...
                i_printStrCell(obj.AvailableWebcams));
            fprintf('           I2CBusSpeed: %-30d\n',obj.I2CBusSpeed);
            fprintf('\n%s\n',getFooter(obj));
        end
        
        function s = getFooter(obj) %#ok<MANU>
            s = sprintf(['  <a href="matlab:raspi.internal.helpView', ...
                '(''raspberrypiio'',''RaspiSupportedPeripherals'')">', ...
                'Supported peripherals</a>\n']);
        end
        
        function req = createRequest(obj, requestId, varargin)
            payload = uint8([]);
            if nargin > 0
                for i = 1:nargin-2
                    if ismember(class(varargin{i}),{'char', 'logical'})
                        payload = [payload, uint8(varargin{i})]; 
                    else
                        payload = [payload, typecast(varargin{i}, 'uint8')]; 
                    end
                end
            end
            req = [uint32(requestId), uint32(obj.Sequence), ...
                uint32(length(payload))];
            req = [typecast(req, 'uint8'), payload];
        end
        
        function status = getGPIOPinStatus(obj, pinNumber)
            sendRequest(obj,obj.REQUEST_GPIO_GET_DIRECTION, ...
                uint32(pinNumber));
            resp = recvResponse(obj); % uint8
            status = uint8(resp);
        end
        
        function getAvailablePeripherals(obj)
            %Find available I2C buses
            obj.AvailableI2CBuses = {};
            for i = 1:length(obj.BoardInfo.I2C)
                cmd = ['stat -t --format=%n /dev/i2c-' num2str(obj.BoardInfo.I2C(i).Number)];
                try 
                    execute(obj.Ssh,cmd);
                    obj.AvailableI2CBuses{end+1} = obj.BoardInfo.I2C(i).Name;
                    id = getId(obj.BoardInfo.I2C(i).Name);
                    obj.I2C.(id).Number = obj.BoardInfo.I2C(i).Number;
                    obj.I2C.(id).Pins   = obj.BoardInfo.I2C(i).Pins;
                catch
                end
            end
            if ~isempty(obj.AvailableI2CBuses)
                % Find I2C bus speed
                try
                    ret = execute(obj.Ssh,'sudo cat /sys/module/i2c_bcm2708/parameters/baudrate');
                    obj.I2CBusSpeed = str2double(ret);
                catch ME
                    baseME = MException(message('raspi:utils:CannotGetI2CBusSpeed'));
                    EX = addCause(baseME, ME);
                    warning(EX.identifier, EX.message);
                end
            end
            
            % Find available SPI channels
            obj.AvailableSPIChannels = {};
            obj.SPI(1).Pins = [];
            for i = 1:length(obj.BoardInfo.SPI(1).Channel)
                try
                    execute(obj.Ssh,['stat --format=%n /dev/spidev' ...
                        int2str(obj.BoardInfo.SPI(1).Number) '.' ...
                        int2str(obj.BoardInfo.SPI(1).Channel(i).Number)]);
                    obj.AvailableSPIChannels{end+1} = obj.BoardInfo.SPI(1).Channel(i).Name;
                    id = getId(obj.BoardInfo.SPI(1).Channel(i).Name);
                    obj.SPI(1).Channel.(id).Number = obj.BoardInfo.SPI(1).Channel(i).Number;
                    obj.SPI(1).Channel.(id).Pins   = obj.BoardInfo.SPI(1).Channel(i).Pins;
                catch
                end
            end
            if ~isempty(obj.AvailableSPIChannels)
                obj.SPI(1).Pins = obj.BoardInfo.SPI(1).Pins;
            end
            
            % Remove I2C pins from the list of available GPIO pins
            obj.AvailableDigitalPins = obj.BoardInfo.GPIOPins;
            for i = 1:length(obj.AvailableI2CBuses)
                id = getId(obj.AvailableI2CBuses{i});
                obj.AvailableDigitalPins = ...
                            setdiff(obj.AvailableDigitalPins, ...
                            obj.I2C.(id).Pins);
            end
            
            % Remove SPI pins from the list of available GPIO pins
            obj.AvailableDigitalPins = setdiff(obj.AvailableDigitalPins, ...
                obj.SPI(1).Pins);
            for i = 1:length(obj.AvailableSPIChannels)
                id = getId(obj.AvailableSPIChannels{i});
                obj.AvailableDigitalPins = ...
                    setdiff(obj.AvailableDigitalPins, ...
                    obj.SPI.Channel.(id).Pins);
            end
            
            % Get current state of GPIO pins
            for pin = obj.AvailableDigitalPins
                pinName = getPinName(pin);
                obj.DigitalPin.(pinName).Inuse = false;
                obj.DigitalPin.(pinName).Mode  = obj.PINMODE_UNSET;
            end
            
            % Set available LED's
            obj.AvailableLEDs = {};
            for i = 1:numel(obj.BoardInfo.LED)
                name = obj.BoardInfo.LED(i).Name;
                id = getId(name);
                obj.AvailableLEDs{end+1} = name;
                obj.LED.(id).Number            = i - 1;
                obj.LED.(id).Color             = obj.BoardInfo.LED(i).Color;
                obj.LED.(id).Trigger           = getLEDConfiguration(obj,name);
                obj.LED.(id).AvailableTriggers = getAvailableLEDConfigurations(obj,name);
            end
            
            % Find available Web cameras
            obj.WebcamInfo = obj.getAvailableWebcams();
            if ~isempty(obj.WebcamInfo)
                obj.AvailableWebcams = {obj.WebcamInfo.Name};
            end
        end
        
        function cameraInfo = getAvailableWebcams(obj)
            cameraInfo = [];
            cam = obj.getConnectedWebcamNumber;
            if ~isempty(cam)
                if obj.isV4l2Installed
                    try
                        output = execute(obj.Ssh,'v4l2-ctl --list-devices');
                        tmp = regexp(output, '\n', 'split');
                        indx = [];
                        for i=1:numel(tmp)
                            tmp{i} = strtrim(tmp{i});
                            if isempty(tmp{i})
                                indx(end+1) = i;
                            end
                        end
                        tmp(indx) = [];
                        for i= 1:2:numel(tmp)
                            cameraInfo(end+1).Name = tmp{i}; %#ok<*AGROW>
                            cameraInfo(end).Dev    = tmp{i+1};
                        end
                    catch
                        for i=1:numel(cam)
                            cameraInfo(i).Name = cam{i};
                            cameraInfo(i).Dev  = cam{i};
                        end
                    end
                else
                    if obj.hasInternetAccess
                        try
                            installV4l2(obj);
                            output = execute(obj.Ssh,'v4l2-ctl --list-devices');
                            tmp = regexp(output, '\n', 'split');
                            for i=1:round(numel(tmp)/3)
                                name = regexp(tmp{i}, '(?<name>.+)\s+\(.+\):$', 'tokens', 'once');
                                cameraInfo(i).Name = name{1};
                                cameraInfo(i).Dev  = strtrim(tmp{i+1});
                            end
                        catch
                            for i=1:numel(cam)
                                cameraInfo(i).Name = cam{i};
                                cameraInfo(i).Dev  = cam{i};
                            end
                        end
                    else
                        for i=1:numel(cam)
                            cameraInfo(i).Name = cam{i};
                            cameraInfo(i).Dev  = cam{i};
                        end
                    end
                end
            end
        end
        
       function result = getConnectedWebcamNumber(obj)
            try
                output = execute(obj.Ssh,'ls /dev/video*');
                result = regexp(output, '/dev/video\d+', 'match');
            catch
                result = [];
            end
       end
        
        function checkDigitalPin(obj, pinNumber)
            validateattributes(pinNumber, {'numeric'}, {'scalar'}, ...
                '', 'pinNumber');
            if ~any(obj.AvailableDigitalPins == pinNumber)
                error(message('raspi:utils:UnexpectedDigitalPinNumber'));
            end
        end
        
        function closeAllDigitalPins(obj)
            for pinNumber = obj.AvailableDigitalPins
                pinName = getPinName(pinNumber);
                if obj.DigitalPin.(pinName).Inuse
                    try
                        configurePin(obj,pinNumber,'unset');
                    catch EX
                        warning(EX.identifier, EX.message);
                    end
                end
            end
        end
        
        function output = echo(obj, input)
            sendRequest(obj, obj.REQUEST_ECHO, uint8(input));
            output = recvResponse(obj); % uint8
        end
        
        function version = getServerVersion(obj)
            sendRequest(obj, obj.REQUEST_VERSION);
            version = typecast(recvResponse(obj), 'uint32'); % uint8
        end

        function authorize(obj, hash)
            obj.sendRequest(obj.REQUEST_AUTHORIZATION, [hash, 0]);
            obj.recvResponse;
        end
        
        function ret = isI2CBusAvailable(obj, bus)
            sendRequest(obj, obj.REQUEST_I2C_BUS_AVAILABLE, uint32(bus));
            ret = logical(recvResponse(obj)); % uint8
        end
        
        function ret = isSPIChannelAvailable(obj, spi, channel)
            try
                execute(obj.Ssh, ['stat /dev/spidev', int2str(spi), '.', int2str(channel)]);
                ret = true;
            catch 
                ret = false;
            end
        end
        
        function name = getBoardName(obj)
            %  http://elinux.org/RPi_HardwareHistory
            %  0000 - Beta board
            %  0001 - Not used
            %  0002 - Model B Rev 1
            %  0003 - Model B Rev 1
            %  0004 - Model B Rev 2 
            %  0005 - Model B Rev 2 
            %  0006 - Model B Rev 2
            %  0007 - Model A Rev 2
            %  0008 - Model A Rev 2
            %  0009 - Model A Rev 2
            %  000e - Model B Rev 2 + 512MB
            %  000f - Model B Rev 2 + 512MB
            %  
            %  * 1000 in front of revision indicates overvolting
            try
                ret = execute(obj.Ssh,'cat /proc/cpuinfo');
                hwId = regexp(ret, 'Hardware\s+:\s+BCM(\d+)\s+','tokens','once');
                revno = regexp(ret, 'Revision\s+:\s+([abcdefABCDEF0-9]+)', 'tokens', 'once');
                if isequal(hwId{1},'2709')
                    % Hardware	: BCM2709
                    % This also covers Raspberry Pi 3 which has a BCM2837
                    switch revno{1}(end-3:end)
                        case {'1041'}
                            name = 'Raspberry Pi 2 Model B';
                        case {'2082'}
                            name = 'Raspberry Pi 3 Model B';
                        otherwise
                            % early unknown beta board
                            name = 'Raspberry Pi 2 Model B';
                    end
                else
                    switch revno{1}(end-3:end)
                        case {'0002','0003'}
                            name = 'Raspberry Pi Model B Rev 1';
                        case {'0007','0008','0009'}
                            name = 'Raspberry Pi Model A Rev 2';
                        case {'0004','0005','0006','000d','000e','000f'}
                            name = 'Raspberry Pi Model B Rev 2';
                        case {'0010'}
                            name = 'Raspberry Pi Model B+';
                        otherwise
                            % New board ??
                            name = 'Raspberry Pi Model B+';
                    end
                end
            catch EX
                error(message('raspi:utils:BoardRevision'));
            end
        end
    end
    
    methods (Hidden)
        function delete(obj)
            if obj.Initialized
                if ~isempty(obj.IpNode) && isKey(obj.ConnectionMap, obj.IpNode.Hostname)
                    remove(obj.ConnectionMap, obj.IpNode.Hostname);
                end
                % Don't need to worry about LED. LED is opened/closed at each
                % write.
                try
                    closeAllDigitalPins(obj);
                catch EX
                    warning(EX.identifier, EX.message);
                end
            end
        end
        
        function saveInfo = saveobj(obj)
            saveInfo.DeviceAddress = obj.DeviceAddress; 
        end
    end
    
    methods (Static, Access = protected)
        function file = fullLnxFile(varargin)
            % Convert paths to Linux convention.
            
            file = strrep(varargin{1}, '\', '/');
            for i = 2:nargin
                file = [file, '/', varargin{i}]; 
            end
            file = strrep(file, '//', '/');
            file = regexprep(file, '/$', '');  %remove trailing slash
        end
    end
    
    methods (Static)
        function updateServer(varargin)
            % RASPI.UPDATESERVER updates the MATLAB communication server running on
            % your Raspberry Pi to the latest version compatible with the raspi
            % interface.
            %
            % RASPI.UPDATESERVER(deviceAddress, username, password) updates MATLAB
            % communication server running on the Raspberry Pi with given
            % deviceAddress, username, and password.
            raspi.internal.updateServer(varargin{:});
        end
    end
    
    methods (Static, Hidden)
        function obj = loadobj(saveInfo)
            try
                obj = raspi(saveInfo.DeviceAddress);
            catch EX
                warning(EX.identifier, EX.message);
                obj = raspi.empty;
            end
        end
    end
end

% ----------------------
% Local Functions
% ----------------------

function showImage(imgFile, title)
if ~isempty(imgFile) && exist(imgFile,'file') == 2
    fig = figure( ...
        'Name', title, ...
        'NumberTitle', 'off');
    hax = axes( ...
        'Parent',fig, ...
        'Visible','off');
    imshow(imgFile,'parent',hax,'border','tight');
end
end

function id = getId(name)
id = regexprep(name, '[^\w]', '');
end

function pinName = getPinName(pinNumber)
pinName = ['gpio' int2str(pinNumber)];
end

function EX = getServerException(errno)
try
    EX = MException(message(['raspi:server:ERRNO', num2str(errno)]));
catch
    EX = MException(message('raspi:server:ERRNO'));
end
end

function checkDigitalValue(value)
validateattributes(value, {'numeric', 'logical'}, ...
    {'scalar'}, '', 'value');
if isnumeric(value) && ~((value == 0) || (value == 1))
    error(message('raspi:utils:InvalidDigitalInputValue'));
end
end

function str = i_printStrCell(c)
str = '{';
for k = 1:numel(c)
    str = [str '''' c{k} ''''];
    if k ~= numel(c)
        str = [str ','];
    end
end
str = [str '}'];
end

function str = i_printArray(c)
str = '[';
for k = 1:numel(c)
    str = [str num2str(c(k))];
    if k ~= numel(c)
        str = [str ','];
    end
end
str = [str ']'];
end
