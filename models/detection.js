const mongoose = require('mongoose')

const detectionShema = new mongoose.Schema({
    name:{
        type: String,
        required: true
    },
    device_position:{
        type: Number,
        required: false
    },
    motion:{
        type: Boolean,
        required: false
    },
    switch_code:{
        type: Number,
        required: false
    },
    water_det:{
        type: Boolean,
        required: false
    },
    detectionDate:{
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

module.exports = mongoose.model('Detection', detectionShema)