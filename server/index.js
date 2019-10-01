const express = require('express')
const app = express()
const port = 3000

const root = './dist';
app.get('/*', (req, res) => res.sendFile(req.path, {root}))

app.listen(port, () => console.log(`Example app listening on port ${port}!`))