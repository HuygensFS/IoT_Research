const express = require ('express')
const router = express.Router()
const Detection = require('../models/detection')

//GET ALL
router.get('/', async (req,res) =>{
    try {
        const detections = await Detection.find()
        res.json(detections)
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//GET ONE
router.get('/:id', getDetection, (req,res) =>{
    res.json(res.detection)
})

//GET BY NAME
router.get('/name/:name_val', async (req,res) =>{
    try {
        const detections = await Detection.find({name:req.params.name_val})
        res.json(detections)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})
//GET BY POSITION
router.get('/position/:pos_val', async (req,res) =>{
    try {
        const detections = await Detection.find({device_position:req.params.pos_val})
        res.json(detections)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})
//GET BY NAME AND POSITION
router.get('/name/:name_val/position/:pos_val', async (req,res) =>{
    try {
        const detections = await Detection.find({name:req.params.name_val,device_position:req.params.pos_val})
        res.json(detections)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//CREATE ONE
router.post('/', async (req,res) =>{
    const detection = new Detection({
        name: req.body.name,
        device_position:req.body.device_position,
        motion:req.body.motion,
        switch_code:req.body.switch_code,
        water_det:req.body.water_det,
        timestamp:Math.floor(Date.now()/1000)
    })
    try {
        const newDetection = await detection.save()
        res.status(201).json(newDetection)
    } catch (err) {
        res.status(400).json({ message: err.message })
    }
})

//UPDATE ONE
router.patch('/:id', getDetection, async (req,res) =>{
    if(req.body.name != null){
        res.detection.name = req.body.name
    }
    if(req.body.device_position != null){
        res.detection.device_position = req.body.device_position
    }
    if(req.body.motion != null){
        res.detection.motion = req.body.motion
    }
    if(req.body.switch_code != null){
        res.detection.switch_code = req.body.switch_code
    }
    if(req.body.water_det != null){
        res.detection.water_det = req.body.water_det
    }
    res.detection.timestamp = Math.floor(Date.now()/1000)
    //res.detection.detectionDate = Date.now()
    try {
        const updatedDetection = await res.detection.save()
        res.json(updatedDetection)
    } catch (err){
        res.status(400).json({message: err.message })
    }
})

//DELETE ONE
router.delete('/:id', getDetection, async (req,res) =>{
    try {
        await res.detection.remove()
        res.json({ message: 'Deleted Detection Data'})
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//DELETE UNTIL ONE WEEK
router.delete('/week/clean', async (req,res) =>{
    var time_limit = Math.floor(Date.now()/1000)-604800;
    Detection.remove({timestamp:{$lte : time_limit}},function(err)
    {
        if(!err)
        {
            console.log("Clean complete")
            res.json({ message: 'Deleted Detection Data'})
        }
        else{
            console.log("Clean error")
            res.status(500).json({ message: err.message })
        }
    });
})

async function getDetection(req,res,next){
    let detection
    try {
        detection = await Detection.findById(req.params.id)
        if(detection == null){
            return res.status(404).json({ message: 'Cannot find detection'})
        }
    } catch (err) {
        return res.status(500).json({ message: err.message})
    }

    res.detection = detection
    next()
}

module.exports = router