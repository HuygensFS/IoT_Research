const express = require ('express')
const router = express.Router()
const Sensor = require('../models/sensor')

//GET ALL
router.get('/', async (req,res) =>{
    try {
        const sensors = await Sensor.find()
        res.json(sensors)
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//GET ONE
router.get('/:id', getSensor, (req,res) =>{
    res.json(res.sensor)
})

//GET BY NAME
router.get('/name/:name_val', async (req,res) =>{
    try {
        const sensors = await Sensor.find({name:req.params.name_val})
        res.json(sensors)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})
//GET BY POSITION
router.get('/position/:pos_val', async (req,res) =>{
    try {
        const sensors = await Sensor.find({device_position:req.params.pos_val})
        res.json(sensors)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})
//GET BY NAME AND POSITION
router.get('/name/:name_val/position/:pos_val', async (req,res) =>{
    try {
        const sensors = await Sensor.find({name:req.params.name_val,device_position:req.params.pos_val})
        res.json(sensors)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//CREATE ONE
router.post('/', async (req,res) =>{
    const sensor = new Sensor({
        name: req.body.name,
        temperature: req.body.temperature,
        humidity:req.body.humidity,
        lux:req.body.lux,
        lightlevel:req.body.lightlevel,
        dark:req.body.dark,
        daylight:req.body.daylight,
        device_position:req.body.device_position,
        co2:req.body.co2,
        tvoc:req.body.tvoc,
        timestamp:Math.floor(Date.now()/1000)
    })
    try {
        const newSensor = await sensor.save()
        res.status(201).json(newSensor)
    } catch (err) {
        res.status(400).json({ message: err.message })
    }
})

//UPDATE ONE
router.patch('/:id', getSensor, async (req,res) =>{
    if(req.body.name != null){
        res.sensor.name = req.body.name
    }
    if(req.body.temperature != null){
        res.sensor.temperature = req.body.temperature
    }
    if(req.body.humidity != null){
        res.sensor.humidity = req.body.humidity
    }
    if(req.body.lux != null){
        res.sensor.lux = req.body.lux
    }
    if(req.body.lightlevel != null){
        res.sensor.lightlevel = req.body.lightlevel
    }
    if(req.body.dark != null){
        res.sensor.dark = req.body.dark
    }
    if(req.body.daylight != null){
        res.sensor.daylight = req.body.daylight
    }
    if(req.body.device_position != null){
        res.sensor.device_position = req.body.device_position
    }
    if(req.body.co2 != null){
        res.sensor.co2 = req.body.co2
    }
    if(req.body.tvoc != null){
        res.sensor.tvoc = req.body.tvoc
    }
    res.sensor.timestamp = Math.floor(Date.now()/1000)
    //res.sensor.sensorDate = Date.now()
    try {
        const updatedSensor = await res.sensor.save()
        res.json(updatedSensor)
    } catch (err){
        res.status(400).json({message: err.message })
    }
})

//DELETE ONE
router.delete('/:id', getSensor, async (req,res) =>{
    try {
        await res.sensor.remove()
        res.json({ message: 'Deleted Sensor Data'})
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//DELETE UNTIL ONE WEEK
router.delete('/week/clean', async (req,res) =>{
    var time_limit = Math.floor(Date.now()/1000)-604800;
    Sensor.remove({timestamp:{$lte : time_limit}},function(err)
    {
        if(!err)
        {
            console.log("Clean complete")
            res.json({ message: 'Deleted Sensor Data'})
        }
        else{
            console.log("Clean error")
            res.status(500).json({ message: err.message })
        }
    });
})

async function getSensor(req,res,next){
    let sensor
    try {
        sensor = await Sensor.findById(req.params.id)
        if(sensor == null){
            return res.status(404).json({ message: 'Cannot find sensor'})
        }
    } catch (err) {
        return res.status(500).json({ message: err.message})
    }

    res.sensor = sensor
    next()
}

module.exports = router