<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs12 v-if="connectionEstablished" style="margin-bottom:15px">
                <v-text-field label="Bot IP" v-model="botIp" />
                <v-btn v-if="stopped" @click="start()">Start</v-btn>
                <v-btn v-else @click="stop()">Stop</v-btn>
                <v-btn v-if="images.length > 0" @click="saveImages()">Download Images</v-btn>
            </v-flex>
            <v-flex xs6 style='min-height:500px;min-width:500px'>
                <img 
                    v-if="images.length > 0"
                    :src="images[selectedImageIndex].withHeader || images[0] && images[0].withHeader" />
            </v-flex>
            <v-flex xs6  style='min-height:500px;min-width:500px'>
                <img
                    v-if="processedImages.length > 0"
                    :src="processedImages[selectedImageIndex].withHeader || processedImages[0] && processedImages[0].withHeader" />
            </v-flex>
            <v-flex xs6 >
                <v-layout wrap>
                    <v-flex xs1 v-for="(i, index) in images" :key="i.id">
                        <img 
                            :src="i.withHeader"
                            height="50px"
                            width="50px"
                            @click="selectedImageIndex = index"
                            :style="{
                                cursor: 'pointer',
                                border: selectedImageIndex == index ? '2px solid red':'none'
                            }"
                        />
                    </v-flex>
                </v-layout>
            </v-flex>
            <v-flex xs6 >
                <v-layout wrap>
                    <v-flex xs1 v-for="(i, index) in processedImages" :key="i.id">
                        <img 
                            :src="i.withHeader"
                            height="50px"
                            width="50px"
                            @click="selectedImageIndex = index"
                            :style="{
                                cursor: 'pointer',
                                border: selectedImageIndex == index ? '2px solid red':'none'
                            }"
                        />
                    </v-flex>
                </v-layout>
            </v-flex>
        </v-layout>
        
    </v-container>
</template>

<script>
import base64Img from 'base64-img'
import uuid from 'uuid/v4'
import fs from 'fs'
import moment from 'moment'
import people_pics from './people_pics'

function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    return new Blob(byteArrays, { type: contentType });
}

export default {
    data() {
        return {
            botIp: "10.10.0.7",
            loadingPicture: false,
            images: [],
            processedImages: [],
            stopped: true,
            selectedImageIndex: 0,
            socket: new WebSocket('ws://localhost:8765'),
            connectionEstablished: false
        }
    },
    mounted () {
        this.setupWebsockets();
    },
    methods: {
        setupWebsockets() {
            // Listen for incoming base64 ascii data to display
            this.socket.addEventListener('message', (event) => {
                console.log('recieved message');
                console.log(event);
                const withoutHeader = event.data;
                const withHeader = 'data:image/png;base64,' + event.data;
                this.processedImages.push({withoutHeader, withHeader, id: uuid()})
            });

            this.socket.addEventListener('open', (event) => {
                console.log('websocket connection established');
                console.log(event);
                this.connectionEstablished = true;
                // this.test()
            });
        },
        test() {
            // use this test when working on the ui so you don't need to connect 
            // to a camera. Each people_pic is a base64 string
            people_pics.forEach(people_pic => {
                this.images.push({
                    withHeader: 'data:image/png;base64,' + people_pic, 
                    withoutHeader: people_pic, 
                    id: uuid()
                })
                this.socket.send(people_pic)
            });
        },
        start() {
            this.stopped = false;
            this.takePictures();
        },
        stop() {
            this.stopped = true;
            this.loadingPicture = false;
        },
        takePictures () {
            Promise.race([
                fetch(`http://${this.botIp}/api/cameras/rgb?base64=true&fileName=asdf&width=500&height=500&displayOnScreen=true&overwriteExisting=false`, {
                    method: 'GET'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => response.json())
            .then(jsonData => {
                console.log(jsonData);
                // the base64toBlob helper expects an encoding without the header
                // so we just store both so they can be easily displayed
                // and saved as well
                const withoutHeader = jsonData.result.base64;
                const withHeader = 'data:image/png;base64,' + jsonData.result.base64;
                this.images.unshift({withoutHeader, withHeader, id: uuid()});
                this.socket.send(withoutHeader)
                this.loadingPicture = false;
                if (!this.stopped) {
                    setTimeout(this.takePictures, 1000);
                }
            })
            .catch(err => {
                console.log(err);
                this.stopped = true;
            })
        },
        saveImages () {
            this.images.forEach((image, index) => {
                this.saveFile(image.withoutHeader, index + "-" + moment().format() + ".png");
            });
            // this.processedImages.forEach((image, index) => {
            //     this.saveFile(image.withoutHeader, index + "-" + moment().format() + ".png");
            // });
        },
        saveFile(base64Data, filename) {
            var file = base64toBlob(base64Data, "image/png");
            if (window.navigator.msSaveOrOpenBlob)
                // IE10+
                window.navigator.msSaveOrOpenBlob(file, filename);
            else {
                // Others
                var a = document.createElement("a"),
                url = URL.createObjectURL(file);
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                setTimeout(function() {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                }, 0);
            }
        },
    },

}
</script>