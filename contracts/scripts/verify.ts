import { ethers } from "hardhat";
import { run } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
    console.log("🔍 Starting contract verification...\n");

    // Get deployment info
    const network = await ethers.provider.getNetwork();
    const networkName = network.name;
    const deploymentFile = path.join(__dirname, "../deployments", `${networkName}.json`);

    if (!fs.existsSync(deploymentFile)) {
        console.error("❌ Deployment file not found. Please run deployment first.");
        process.exit(1);
    }

    const deploymentInfo = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
    console.log(`📋 Verifying contract: ${deploymentInfo.address}`);
    console.log(`🌐 Network: ${networkName}\n`);

    try {
        // Verify the contract
        console.log("🔨 Running verification...");

        await run("verify:verify", {
            address: deploymentInfo.address,
            constructorArguments: [
                deploymentInfo.functionsRouter,
                deploymentInfo.donId,
                deploymentInfo.subscriptionId,
            ],
        });

        console.log("✅ Contract verification successful!");
        console.log("\n🔗 View contract on SnowTrace:");
        if (network.chainId === 43114n) {
            console.log(`   https://snowtrace.io/address/${deploymentInfo.address}`);
        } else if (network.chainId === 43113n) {
            console.log(`   https://testnet.snowtrace.io/address/${deploymentInfo.address}`);
        }

    } catch (error) {
        console.error("❌ Verification failed:", error);
        process.exit(1);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Script execution failed:", error);
        process.exit(1);
    }); 