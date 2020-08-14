require('dotenv').config()

const express = require('express')
const app = express()
const mongoose = require('mongoose')

mongoose.connect(process.env.DATABASE_URL, { useNewUrlParser: true })
const db = mongoose.connection
db.on('error', (error) => console.error(error))
db.once('open', (error) => console.log('Connected to Database'))

app.use(express.json())

const sensorsRouter = require('./routes/sensors')
const sequencesRouter = require('./routes/sequences')
const detectionsRouter = require('./routes/detections')
app.use('/sensors', sensorsRouter)
app.use('/sequences', sequencesRouter)
app.use('/detections', detectionsRouter)

app.listen(3000, () => console.log('Server has started'))