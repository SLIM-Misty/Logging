# logging

## Object Detection Pipeline Setup
The object detection can be found in the /script folder. I needs to be in the
tensorflow object_detection folder to work properly due to having some relative pathnames
to packages contained in that folder. 

Start by cloning the models repo.
```
cd scripts
git clone https://github.com/tensorflow/models/
```

Now you will need to setup the object_dection model via protobufs. Follow [this tutorial](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) to set it up. More information on using the object_detection framework can be found in the README [here](https://github.com/tensorflow/models/tree/master/research/object_detection).

Once you have the model setup, copy misty_object_detection.py to the object_detection folder and run it.
```
mv misty_object_detection.py ./models/research/object_detection
```

The script has a websocket which listens to localhost:8765. It expects base64 rgb image data. Dimensions of the image don't matter. You will need this script running for the /takepicture route to work properly.

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Run your end-to-end tests
```
npm run test:e2e
```

### Run your unit tests
```
npm run test:unit
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
