<template>
    <div>takepicture</div>
</template>

<script>

const ip = '10.10.0.7';
let socket = new LightSocket(ip, openCallback);
let subscribed = null;

async function openCallback() {
    socket.Unsubscribe("FaceRecognition");
    subscribed = false;
    await sleep(8000);
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export default {
    data: () => {
        return {
            botIp: ''
        }
    },
    mounted: () => {
        //GET http://{ip.address}/api/cameras/rgb?base64=false&fileName=&width=null&height=null&displayOnScreen=false&overwriteExisting=false
        Promise.race([
            fetch(`http://${this.botIp}/api/cameras/rgb?base64=true&fileName=asdf.jpg&width=500&height=500&displayOnScreen=true&overwriteExisting=false`, {
                method: 'GET'
            }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
        ])
        .then(response => response.json())
        .then(jsonData => console.log(jsonData))
    }

}