// Use IIFE to avoid the global context pollution
(() => {
  let interval = 500;
  let accuracy = 10;
  let password = '';
  const browserInfo = bowser.parse(window.navigator.userAgent);
  const device_id = uuidv4();
  const acceleration = {x: 0, y: 0, z: 0, };
  const gyroscope = {x: 0, y: 0, z: 0, };
  const orientation = {x: 0, y: 0, z: 0, oc: 0, };
  const AxDom = $('#accelerationX > div > span');
  const AyDom = $('#accelerationY > div > span');
  const AzDom = $('#accelerationZ > div > span');
  const RxDom = $('#gyroscopeX > div > span');
  const RyDom = $('#gyroscopeY > div > span');
  const RzDom = $('#gyroscopeZ > div > span');
  const OxDom = $('#orientationX > div > span');
  const OyDom = $('#orientationY > div > span');
  const OzDom = $('#orientationZ > div > span');
  const deviceMotionEventCallbackFunction = (deviceMotionEvent) => {
    let accelerationOnXAxis =
      deviceMotionEvent.accelerationIncludingGravity.x || 0;
    let accelerationOnYAxis =
      deviceMotionEvent.accelerationIncludingGravity.y || 0;
    let accelerationOnZAxis =
      deviceMotionEvent.accelerationIncludingGravity.z || 0;
    acceleration.x = Math.round(accelerationOnXAxis * accuracy) / accuracy;
    acceleration.y = Math.round(accelerationOnYAxis * accuracy) / accuracy;
    acceleration.z = Math.round(accelerationOnZAxis * accuracy) / accuracy;

    let gyroscopeOnXAxis = deviceMotionEvent.rotationRate.beta;
    let gyroscopeOnYAxis = deviceMotionEvent.rotationRate.gamma;
    let gyroscopeOnZAxis = deviceMotionEvent.rotationRate.alpha;
    gyroscope.x = Math.round(gyroscopeOnXAxis * accuracy) / accuracy;
    gyroscope.y = Math.round(gyroscopeOnYAxis * accuracy) / accuracy;
    gyroscope.z = Math.round(gyroscopeOnZAxis * accuracy) / accuracy;
  };
  const deviceOrientationEventCallbackFunction = (deviceOrientationEvent) => {
    let arrowObj = $('#arrow');

    if (deviceOrientationEvent.webkitCompassHeading) {
      // oc: orientation compass
      orientation.oc =
        Math.ceil(deviceOrientationEvent.webkitCompassHeading) || 0;
    } else {
      orientation.oc =
        Math.round((deviceOrientationEvent.alpha || 0) * accuracy) / accuracy;
    }

    orientation.x =
      Math.round((deviceOrientationEvent.alpha || 0) * accuracy) / accuracy;
    orientation.y =
      Math.round((deviceOrientationEvent.beta || 0) * accuracy) / accuracy;
    orientation.z =
      Math.round((deviceOrientationEvent.gamma || 0) * accuracy) / accuracy;
    // FIXME: The compass does not point to the right direction on the Android devices.
    arrowObj.css('transform', `rotate(${360 - orientation.oc}deg)`);
  };

  function addEventCallbackFunction() {
    [{'event': 'DeviceMotionEvent',
      'eventName': 'devicemotion',
      'eventHandler': deviceMotionEventCallbackFunction,
     },
     {'event': 'DeviceOrientationEvent',
      'eventName': 'deviceorientation',
      'eventHandler': deviceOrientationEventCallbackFunction,
    }].forEach(
      (obj) => {
        let deviceEvent = window[obj.event];

        // See: https://tinyurl.com/y3phm82o
        if ((typeof deviceEvent.requestPermission) === 'function') {
          /*
           * Call the permission requesting API to ask the permission.
           */
          deviceEvent.requestPermission()
            .then((response) => {
              if (response == 'granted') {
                window.addEventListener(obj.eventName, obj.eventHandler);
              }
            })
            .catch((error) => {
              console.error(error);
            });
        } else {
          window.addEventListener(obj.eventName, obj.eventHandler);
        }
      }
    );
  }

  function addCleanupFunction(deviceName) {
    document.onvisibilitychange = () => {
      if (document.visibilityState == 'hidden') {
        /*******************************************************************
        * According to this article: https://tinyurl.com/yc6h5z5k          *
        * The unload, the beforeunload and the pagehide events will not    *
        * be fired on the mobile devices. Also, that article also suggests *
        * that treat the hidden state as the last state on                 *
        * the mobile devices.                                              *
        * The hidden state is related to the visibilitychange event, For   *
        * more detail, please check https://tinyurl.com/yy2gjbad           *
        * To deal with this situation, I add an event handler for the      *
        * visibilitychange event to issue the deregister request and       *
        * re-register.                                                     *
        ********************************************************************/
        deregister();
      } else if (document.visibilityState == 'visible') {
        register(deviceName);
      }
    }

    if (browserInfo.browser.name == 'Safari') {
      // See: https://tinyurl.com/y5d7dv8r
      window.onpagehide = (pagehideEvent) => {
        deregister();
      };
    }
  }

//  FIXME to enable Vibration.
//  function onData(idf_name, data) {
//    if (idf_name == 'Vibration-O') {
//      console.log(data[0]);
//      if (data[0] > 0) {
//        navigator.vibrate(data[0] * 100);
//      }
//    }
//  }


  function onRegister(result, d_name, pw) {
    console.info('register:', result);
    password = pw;
    $('#pageTitle').text(result ? d_name : 'Registration failed');
    const deviceName = d_name;

    if (result) {
      requestAnimationFrame(renderSensorValue);
      setInterval(pushDataToIoTtalk, interval);
      //addCleanupFunction(deviceName);
    }
  }


  function renderSensorValue() {
    AxDom.text(acceleration.x);
    AyDom.text(acceleration.y);
    AzDom.text(acceleration.z);

    RxDom.text(gyroscope.x);
    RyDom.text(gyroscope.y);
    RzDom.text(gyroscope.z);

    OxDom.text(orientation.x);
    OyDom.text(orientation.y);
    OzDom.text(orientation.z);

    requestAnimationFrame(renderSensorValue);
  }


  function pushDataToIoTtalk() {
    csmapi.push(device_id, password, 'Acceleration', [acceleration.x, acceleration.y, acceleration.z, ]);
    csmapi.push(device_id, password, 'Gyroscope'   , [gyroscope.x, gyroscope.y, gyroscope.z, ]);
    csmapi.push(device_id, password, 'Orientation' , [orientation.x, orientation.y, orientation.z, ]);
  }

  function deregister() {
    csmapi.deregister(device_id);
  }


  function promptInputbox() {
    let deviceName = '';

    do {
      deviceName = window.prompt('Please enter the device name',
                                 `${Math.floor(Math.random() * 100)}.SmartPhone`);
    } while ( !deviceName );

    return deviceName;
  }


  function register(d_name){
    csmapi.set_endpoint (window.location.origin);
    var profile = {
        'dm_name': 'Smartphone',    
        'df_list': ['Acceleration', 'Gyroscope', 'Orientation', 'Vibration-O'],            
        'u_name': 'yb',
        'd_name': d_name,
        };
    csmapi.register(device_id, profile, onRegister)        
  };
  
  
  if (!window.DeviceMotionEvent || !window.DeviceOrientationEvent) {
    alert('Your device does not support getting acceleration info from the browser');
    $('#pageTitle').text('Browser not supported')
  } else {
    const deviceName = promptInputbox();

    if (browserInfo.os.name == 'iOS') {
      /*
       * On the iOS-based devices, we need to get the permission grant
       * to access the acceleration, gryoscope information.
       * Also, this permission asking must be triggered by some specific events.
       * These events is listed on this webiste: https://tinyurl.com/y5mrw7pz
       */
      $('#permissionAskingBox').modal('show');
      $('#denyPermission').click(() => {
        $('#pageTitle').text('Permission denied');
      });
      $('#grantPermission').click(() => {
        addEventCallbackFunction();
        register(deviceName);
      });
    } else {
      addEventCallbackFunction();
      register(deviceName);
    }
  }


  function close_page(result){
    if (result){ console.log('Deregister successfully.');}
    else{ console.log('Failed to deregister!');}
    setTimeout("document.location.href=window.location.origin", 100 )
  }


  $('#closePage').click(() => {
    csmapi.deregister(device_id, close_page);
  });


  //  FIXME It is work for page close, but not work for browser close in the mobile phone.
  window.onbeforeunload = function () {
      deregister();
  };
  window.addEventListener("beforeunload", function (e) {
    var confirmationMessage = "Exit?";
    (e || window.event).returnValue = confirmationMessage; //Gecko + IE
    return confirmationMessage;                            //Webkit, Safari, Chrome
  });


})();

