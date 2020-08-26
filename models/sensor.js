const mongoose = require('mongoose')

const sensorShema = new mongoose.Schema({
    name:{
        type: String,
        required: true
    },
    temperature:{
        type: Number,
        required: false
    },
    humidity:{
        type: Number,
        required: false
    },
    lux:{
        type: Number,
        required: false
    },
    lightlevel:{
        type: Number,
        required: false
    },
    dark:{
        type: Boolean,
        required: false
    },
    daylight:{
        type: Boolean,
        required: false
    },
    device_position:{
        type: Number,
        required: false
    },
    co2:{
        type: Number,
        required: false
    },
    tvoc:{
        type: Number,
        required: false
    },
    sensorDate:{
        type: Date,
        required: true,
        default: Date.now
    },
    timestamp:{
        type: Number,
        required: true,
        default: Math.floor(Date.now()/1000)
    }
})

module.exports = mongoose.model('Sensor', sensorShema)