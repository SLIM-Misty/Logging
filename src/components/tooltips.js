export default {
    ActuatorPosition: `Provides information about the position of the actuators 
    responsible for controlling the movement of Misty's head and arms.`,
    AudioPlayComplete: `Sent every time Misty finishes playing an audio file. 
    It is not sent at timed intervals.`,
    BatteryCharge: `Provides information about the state of Misty's battery, 
    including charge percentage, voltage, and charging status. Sends messages at timed 
    intervals of five seconds`,
    BumpSensor: `Sends information each time one of the bump sensors on Misty's 
    base is pressed or released`,
    DriveEncoders: `Provides information about the angular velocity (in degrees per second) 
    and rotation (in degrees) for Misty's left and right encoders.`,
    FaceRecognition: `If face recognition is running on the robot, and a previously 
    trained face is recognized, the PersonName value is the name previously assigned 
    to that face. The PersonName value is unknown_person if an untrained/unknown face is 
    detected. The PersonName value is null if face recognition is not currently running.`,
    FaceTraining: `Sends messages from Misty's computer vision service with information 
    about the status the face training process`,
    HaltCommand: `Sent every time the robot stops and contains the date and time of the 
    event. It is not sent at timed intervals.`,
    IMU: `Provides information from Misty's Inertial Measurement Unit (IMU) sensor. It 
    includes information about the pitch, yaw, and roll orientation angles of the sensor(in degrees) 
    the force(in meters per second) currently applied to the sensor along its pitch, yaw, 
    and roll rotational axes the force(in meters per second squared) currently applied to 
    the sensor along its X, Y, and Z axes`,
    LocomotionCommand: `Sent every time the linear or angular velocity of the robot changes. 
    It is not sent at timed intervals.`,
    SerialMessage: `Provides information sent to Misty by external hardware connected 
    to the ports on her back. SerialMessage events trigger when Misty receives data sent 
    through one of these ports`,
    SkillData: `Subscribe to the SkillData named object to see debug messages, error messages, 
    and other data JavaScript skills publish during skill execution. Use the misty.Debug() 
    command in a skill to send a SkillData message.`,
    TimeOfFlight: `Misty has four edge and four range time-of-flight sensors that provide a 
    single stream of raw proximity data. These sensors send TimeOfFlight messages that you can 
    subscribe to in your skills and robot applications`,
    TouchSensor: `Sends information each time one of the capacitive touch sensors on Misty's 
    head is touched or released`,
    // these events are in BETA
    KeyPhraseRecognized: `Misty sends KeyPhraseRecognized event messages when she recognizes 
    the 'Hey, Misty!' key phrase`,
    SourceTrackDataMessage: `Provides information about the location and volume of the noise 
    or spoken voice that Misty can detect`,
    SourceFocusConfigMessage: `Provides meta information about the configuration of audio 
    localization data. The system only sends this message once, when Misty starts recording audio.`,
    // these events are in ALPHA
    HazardNotification: `Sent each time the hazard system detects a change to a hazard state. 
    You can subscribe to HazardNotification events to be notified when Misty enters or exits 
    a specific hazard state. Hazard states: bumpSensorsHazardState, criticalInternalError, 
    currentSensorsHazard, driveStopped, motorStallHazard, timeOfFlightSensorsHazardState, 
    excessiveSpeedHazard`,
    SlamStatus: `Provides information about the current status of Misty's simultaneous 
    localization and mapping (SLAM) system`,
    SelfState: `Provides a variety of data about Misty’s current internal state, including
     battery charge, voltage, and charging status address affect position and orientation(pose)
      SLAM status sensor messages`,
    WorldState: `(still in early development and can't be used for much at this time. 
    Many of the properties Misty sends in WorldState event messages are reserved for future use, 
    and may have null or invalid values) Exists to provide information about things Misty perceives 
    in her environment.`
}