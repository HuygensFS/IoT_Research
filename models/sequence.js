const mongoose = require('mongoose')

const sequenceShema = new mongoose.Schema({
    seq_json:{
        type: String,
        required: true
    },
    sequenceDate:{
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

module.exports = mongoose.model('Sequence', sequenceShema)