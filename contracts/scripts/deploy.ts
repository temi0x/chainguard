import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
    console.log("🚀 Starting ChainGuard Risk Oracle deployment...\n");

    // Get deployer account
    const [deployer] = await ethers.getSigners();
    console.log(`📋 Deploying contracts with account: ${deployer.address}`);
    console.log(`💰 Account balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} AVAX\n`);

    // Configuration - Update these values for your deployment
    const config = {
        // Chainlink Functions configuration
        functionsRouter: process.env.FUNCTIONS_ROUTER_ADDRESS || "0x0000000000000000000000000000000000000000",
        donId: process.env.DON_ID || "0x0000000000000000000000000000000000000000000000000000000000000000",
        subscriptionId: process.env.SUBSCRIPTION_ID || "0",

        // Gas configuration
        gasLimit: 300000,
    };

    console.log("📝 Deployment Configuration:");
    console.log(`   Functions Router: ${config.functionsRouter}`);
    console.log(`   DON ID: ${config.donId}`);
    console.log(`   Subscription ID: ${config.subscriptionId}`);
    console.log(`   Gas Limit: ${config.gasLimit}\n`);

    try {
        // Deploy ChainGuard Risk Oracle
        console.log("🔨 Deploying ChainGuard Risk Oracle...");

        const ChainGuardRiskOracle = await ethers.getContractFactory("ChainGuardRiskOracle");
        const riskOracle = await ChainGuardRiskOracle.deploy(
            config.functionsRouter,
            config.donId,
            config.subscriptionId,
            {
                gasLimit: config.gasLimit,
            }
        );

        console.log(`⏳ Waiting for deployment confirmation...`);
        await riskOracle.waitForDeployment();

        const deployedAddress = await riskOracle.getAddress();
        console.log(`✅ ChainGuard Risk Oracle deployed to: ${deployedAddress}\n`);

        // Verify deployment
        console.log("🔍 Verifying deployment...");
        const deployedCode = await ethers.provider.getCode(deployedAddress);
        if (deployedCode === "0x") {
            throw new Error("Contract deployment failed - no code at address");
        }
        console.log("✅ Contract verification successful\n");

        // Get deployment info
        const deploymentInfo = {
            network: await ethers.provider.getNetwork(),
            contract: "ChainGuardRiskOracle",
            address: deployedAddress,
            deployer: deployer.address,
            functionsRouter: config.functionsRouter,
            donId: config.donId,
            subscriptionId: config.subscriptionId,
            deploymentTime: new Date().toISOString(),
            blockNumber: await ethers.provider.getBlockNumber(),
        };

        // Save deployment info
        const deploymentPath = path.join(__dirname, "../deployments");
        if (!fs.existsSync(deploymentPath)) {
            fs.mkdirSync(deploymentPath, { recursive: true });
        }

        const networkName = deploymentInfo.network.name;
        const deploymentFile = path.join(deploymentPath, `${networkName}.json`);
        fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

        console.log("📄 Deployment information saved to:", deploymentFile);
        console.log("\n🎉 Deployment completed successfully!");
        console.log("\n📋 Next Steps:");
        console.log("1. Update the contract address in frontend/src/contracts/config.ts");
        console.log("2. Configure Chainlink Functions secrets");
        console.log("3. Test the contract integration");
        console.log("\n🔗 Contract on SnowTrace:");
        const networkId = deploymentInfo.network.chainId;
        if (networkId === 43114n) {
            console.log(`   https://snowtrace.io/address/${deployedAddress}`);
        } else if (networkId === 43113n) {
            console.log(`   https://testnet.snowtrace.io/address/${deployedAddress}`);
        }

    } catch (error) {
        console.error("❌ Deployment failed:", error);
        process.exit(1);
    }
}

// Handle script execution
main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Script execution failed:", error);
        process.exit(1);
    }); 