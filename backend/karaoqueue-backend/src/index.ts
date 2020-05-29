import "reflect-metadata";
import { createExpressServer } from "routing-controllers";
import { QueueController } from "./controllers/queue.controller";
import { SongController } from "./controllers/songs.controller";
import { StatisticsController } from "./controllers/statistics.controller";
import { AuthenticationController } from "./controllers/auth.controller";
import { RpcController } from "./controllers/rpc.controller";

const app = createExpressServer({
    routePrefix: "/api",
    cors: true,
    controllers: [QueueController, SongController, StatisticsController, AuthenticationController, RpcController]
});

app.listen(3000);