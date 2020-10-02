import "reflect-metadata";
import { Request, Response } from "express";
import { Action, createExpressServer } from "routing-controllers";
import { QueueController } from "./controllers/queue.controller";
import { SongController } from "./controllers/songs.controller";
import { StatisticsController } from "./controllers/statistics.controller";
import { AuthenticationController } from "./controllers/auth.controller";
import { RpcController } from "./controllers/rpc.controller";
import jwt from "jsonwebtoken";


import * as dotenv from "dotenv";
dotenv.config();

const app = createExpressServer({
    routePrefix: "/api",
    cors: true,
    authorizationChecker: async (action: Action) => {
        const req: Request = action.request;
        const secret = process.env.KQUEUE_JWTSECRET;
        const token = parseCookies(req.headers.cookie)["jwt"];
        if (token) {
            try {
                const verificationResponse = jwt.verify(token, secret);
                if (verificationResponse) {
                    return true;
                } else {
                    return false;
                }
            } catch (error) {
                return false;
            }
        } else {
            return false;
        }
        
    },
    controllers: [QueueController, SongController, StatisticsController, AuthenticationController, RpcController]
});
app.listen(process.env.KQUEUE_PORT);

function parseCookies(str) {
    let rx = /([^;=\s]*)=([^;]*)/g;
    let obj = {};
    for (let m; m = rx.exec(str);)
        obj[m[1]] = decodeURIComponent(m[2]);
    return obj;
}