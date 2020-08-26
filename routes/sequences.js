const express = require ('express')
const router = express.Router()
const Sequence = require('../models/sequence')

//GET ALL
router.get('/', async (req,res) =>{
    try {
        const sequences = await Sequence.find()
        res.json(sequences)
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//GET ONE
router.get('/:id', getSequence, (req,res) =>{
    res.json(res.sequence)
})

//GET BY Sequence
router.get('/seq/:seq_val', async (req,res) =>{
    try {
        const sequences = await Sequence.find({seq_json:req.params.seq_val})
        res.json(sequences)
        
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//CREATE ONE
router.post('/', async (req,res) =>{
    const sequence = new Sequence({
        seq_json: req.body.seq_json,
        timestamp:Math.floor(Date.now()/1000)
    })
    try {
        const newSequence = await sequence.save()
        res.status(201).json(newSequence)
    } catch (err) {
        res.status(400).json({ message: err.message })
    }
})

//UPDATE ONE
router.patch('/:id', getSequence, async (req,res) =>{
    if(req.body.seq_json != null){
        res.sequence.seq_json = req.body.seq_json
    }
    res.sequence.timestamp = Math.floor(Date.now()/1000)
    //res.sequence.sequenceDate = Date.now()
    try {
        const updatedSequence = await res.sequence.save()
        res.json(updatedSequence)
    } catch (err){
        res.status(400).json({message: err.message })
    }
})

//DELETE ONE
router.delete('/:id', getSequence, async (req,res) =>{
    try {
        await res.sequence.remove()
        res.json({ message: 'Deleted Sequence Data'})
    } catch (err) {
        res.status(500).json({ message: err.message })
    }
})

//DELETE UNTIL ONE WEEK
router.delete('/week/clean', async (req,res) =>{
    var time_limit = Math.floor(Date.now()/1000)-604800;
    Sequence.remove({timestamp:{$lte : time_limit}},function(err)
    {
        if(!err)
        {
            console.log("Clean complete")
            res.json({ message: 'Deleted Sequence Data'})
        }
        else{
            console.log("Clean error")
            res.status(500).json({ message: err.message })
        }
    });
})

async function getSequence(req,res,next){
    let sequence
    try {
        sequence = await Sequence.findById(req.params.id)
        if(sequence == null){
            return res.status(404).json({ message: 'Cannot find sequence'})
        }
    } catch (err) {
        return res.status(500).json({ message: err.message})
    }

    res.sequence = sequence
    next()
}

module.exports = router