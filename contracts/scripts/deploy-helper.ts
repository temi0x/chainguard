import { ethers } from "hardhat";
import * as readline from "readline";

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

function question(query: string): Promise<string> {
    return new Promise((resolve) => {
        rl.question(query, resolve);
    });
}

async function main() {
    console.log("🚀 ChainGuard Risk Oracle Deployment Helper\n");

    try {
        // Check if private key is set
        if (!process.env.PRIVATE_KEY) {
            console.log("⚠️  PRIVATE_KEY environment variable not set.");
            const privateKey = await question("Enter your private key (without 0x): ");
            process.env.PRIVATE_KEY = privateKey;
        }

        // Get network choice
        console.log("\n🌐 Select deployment network:");
        console.log("1. Avalanche Fuji Testnet (Recommended for testing)");
        console.log("2. Avalanche C-Chain Mainnet");
        console.log("3. Local Hardhat Network");

        const networkChoice = await question("\nEnter your choice (1-3): ");

        let network: string;
        switch (networkChoice) {
            case "1":
                network = "fuji";
                break;
            case "2":
                network = "avalanche";
                break;
            case "3":
                network = "hardhat";
                break;
            default:
                console.log("❌ Invalid choice. Using Fuji testnet.");
                network = "fuji";
        }

        // Get Chainlink Functions configuration
        console.log("\n🔗 Chainlink Functions Configuration:");

        const functionsRouter = await question("Functions Router Address (or press Enter for default): ") ||
            "0x0000000000000000000000000000000000000000";

        const donId = await question("DON ID (or press Enter for default): ") ||
            "0x0000000000000000000000000000000000000000000000000000000000000000";

        const subscriptionId = await question("Subscription ID (or press Enter for default): ") || "0";

        // Set environment variables
        process.env.FUNCTIONS_ROUTER_ADDRESS = functionsRouter;
        process.env.DON_ID = donId;
        process.env.SUBSCRIPTION_ID = subscriptionId;

        // Confirm deployment
        console.log("\n📋 Deployment Summary:");
        console.log(`   Network: ${network}`);
        console.log(`   Functions Router: ${functionsRouter}`);
        console.log(`   DON ID: ${donId}`);
        console.log(`   Subscription ID: ${subscriptionId}`);

        const confirm = await question("\nProceed with deployment? (y/N): ");

        if (confirm.toLowerCase() !== "y" && confirm.toLowerCase() !== "yes") {
            console.log("❌ Deployment cancelled.");
            rl.close();
            return;
        }

        // Run deployment
        console.log("\n🚀 Starting deployment...");

        // Import and run the main deployment script
        const { execSync } = require("child_process");
        execSync(`npx hardhat run scripts/deploy.ts --network ${network}`, {
            stdio: "inherit",
            env: { ...process.env }
        });

        // Ask about verification
        const verify = await question("\nWould you like to verify the contract on SnowTrace? (y/N): ");

        if (verify.toLowerCase() === "y" || verify.toLowerCase() === "yes") {
            console.log("\n🔍 Starting verification...");
            execSync(`npx hardhat run scripts/verify.ts --network ${network}`, {
                stdio: "inherit",
                env: { ...process.env }
            });
        }

        console.log("\n✅ Deployment process completed!");
        console.log("\n📋 Next Steps:");
        console.log("1. Update the contract address in frontend/src/contracts/config.ts");
        console.log("2. Configure Chainlink Functions secrets");
        console.log("3. Test the contract integration");

    } catch (error) {
        console.error("❌ Deployment helper failed:", error);
    } finally {
        rl.close();
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Script execution failed:", error);
        process.exit(1);
    }); 