const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',["/home/joao/Documents/euroage_iot/algorithm/alg_routine.py", 'event_data.json',18000,4,60]);
pythonProcess.stdout.on('data', (data) => {
    console.log(data.toString('utf8'));
});


/*const express = require('express')
const app = express()

app.get('/', (req, res) => {

    const { spawn } = require('child_process');
    const pyProg = spawn('python', ["/home/joao/Documents/euroage_iot/alg_function.py", 'event_data.json',18000,4,60]);

    pyProg.stdout.on('data', function(data) {

        console.log(data.toString());
        res.write(data);
        res.end('end');
    });
})

app.listen(4001, () => console.log('Application listening on port 4000!'))*/