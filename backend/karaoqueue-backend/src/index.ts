import express = require("express");

const app: express.Application = express();

app.get('/', (req, res) => {
    res.send('Hello World!');
    // tslint:disable-next-line: no-console
    console.log(req.headers["user-agent"]);
});
app.listen(3000, () => {
    // tslint:disable-next-line: no-console
    console.log('App is listening on port 3000!');
});