<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs4>
                <v-btn :loading="loadingPicture" @click="takePicture()">Take Picture!</v-btn>
            </v-flex>
            <v-flex xs8>
                <img :src="imageSource" />
            </v-flex>
        </v-layout>
    </v-container>
</template>

<script>
import base64Img from 'base64-img'
import uuid from 'uuid/v4'
import fs from 'fs'

export default {
    data() {
        return {
            imageSource: "",
            loadingPicture: false
        }
    },
    methods: {
        takePicture () {
            this.loadingPicture = true;
            Promise.race([
            fetch(`http://10.10.0.7/api/cameras/rgb?base64=true&fileName=asdf&width=500&height=500&displayOnScreen=true&overwriteExisting=false`, {
                method: 'GET'
            }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
        ])
        .then(response => response.json())
        .then(jsonData => {
            console.log(jsonData);
            const imageBase64 = 'data:image/png;base64,' + jsonData.result.base64;
            this.imageSource = imageBase64;
            this.loadingPicture = false;
            // base64Img.img(imageBase64, './images', uuid(), (arg) => {
            //     console.log(arg);
            // }); 
        })
        }
    },
    mounted()    {
        
    }

}
</script>