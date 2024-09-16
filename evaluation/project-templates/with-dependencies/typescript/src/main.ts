import fs from "fs";

import * as target from "./target.js";
import {myStringify} from "./utils/index.js";
Object.entries(target).forEach(([name, exported]) => global[name] = exported);

$$code$$