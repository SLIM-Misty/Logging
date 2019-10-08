<template>
    <v-container>
        <v-layout wrap>
            <v-flex xs4>
                <v-text-field label="Bot IP" v-model="botIp" />
                <v-btn @click="redLED()">Start Routine</v-btn>
            </v-flex>
            <v-flex xs8>
                <img :src="imageSource" />
            </v-flex>
        </v-layout>
    </v-container>
</template>

<script>

export default {
    data: () => {
        return {
            botIp: '10.10.0.7'
        }
    },
    methods: {
        redLED () {
            Promise.race([
                fetch(`http://${this.botIp}/api/led`, {
                    method: 'POST',
                    body: '{ "red":255,"green":0,"blue":0 }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
                setTimeout( () => this.greenLED(), 1000);
            })
            .then(jsonData => console.log(jsonData))
        },
        greenLED () {
            Promise.race([
                fetch(`http://${this.botIp}/api/led`, {
                    method: 'POST',
                    body: '{ "red":0,"green":255,"blue":0 }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
                setTimeout( () => this.blueLED(), 1000);
            })
            .then(jsonData => console.log(jsonData))
        },
        blueLED () {
            Promise.race([
                fetch(`http://${this.botIp}/api/led`, {
                    method: 'POST',
                    body: '{ "red":0,"green":0,"blue":255 }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
                setTimeout( () => this.moveForward(), 1000)
            })
            .then(jsonData => console.log(jsonData))
        },
        moveForward () {
            Promise.race([
                fetch(`http://${this.botIp}/api/drive/time`, {
                    method: 'POST',
                    body: '{ "linearVelocity": 10, "angularVelocity": 0, "timeMS": 4000 }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
                setTimeout(() => this.moveHeadLeft(), 5000)
            })
            .then(jsonData => console.log(jsonData))
        },
        moveHeadLeft () {
            //POST http://10.10.0.7/api/head
            Promise.race([
                fetch(`http://${this.botIp}/api/head`, {
                    method: 'POST',
                    body: '{ "pitch":0,"roll":0,"yaw":100,"velocity":null,"duration":null,"units":"" }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                setTimeout(() => this.moveHeadRight(), 10*1000)
                response.json();
            })
            .then(jsonData => console.log(jsonData))
        },
        moveHeadRight () {
            //POST http://10.10.0.7/api/head
            Promise.race([
                fetch(`http://${this.botIp}/api/head`, {
                    method: 'POST',
                    body: '{ "pitch":0,"roll":0,"yaw":-100,"velocity":null,"duration":null,"units":"" }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 14000))
            ])
            .then(response => {
                setTimeout(() => this.moveArms(), 10000);
                response.json();
            })
            .then(jsonData => console.log(jsonData))
        },
        moveArms () {
            //POST http://10.10.0.7/api/arms/set
            Promise.race([
                fetch(`http://${this.botIp}/api/arms/set`, {
                    method: 'POST',
                    body: '{ "leftArmPosition":30,"rightArmPosition":-30,"leftArmVelocity":null,"rightArmVelocity":null,"duration":1000,"units":"" }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 14000))
            ])
            .then(response => {
                response.json();
                setTimeout(() => this.moveArmsAgain(), 1000);
            })
            .then(jsonData => console.log(jsonData))
        },
        moveArmsAgain () {
            Promise.race([
                fetch(`http://${this.botIp}/api/arms/set`, {
                    method: 'POST',
                    body: '{ "leftArmPosition":-30,"rightArmPosition":30,"leftArmVelocity":null,"rightArmVelocity":null,"duration":20,"units":"" }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
                setTimeout(() => this.moveArmsAgainAgain(), 1000);
            })
            .then(jsonData => console.log(jsonData))
        },
        moveArmsAgainAgain() {
            Promise.race([
                fetch(`http://${this.botIp}/api/arms/set`, {
                    method: 'POST',
                    body: '{ "leftArmPosition":30,"rightArmPosition":-30,"leftArmVelocity":null,"rightArmVelocity":null,"duration":20,"units":"" }'
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
            ])
            .then(response => {
                response.json();
            })
            .then(jsonData => console.log(jsonData))
        }
    },

}
</script>