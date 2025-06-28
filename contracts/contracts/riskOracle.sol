// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {FunctionsClient} from "@chainlink/contracts/src/v0.8/functions/dev/v1_0_0/FunctionsClient.sol";
import {AutomationCompatibleInterface} from "@chainlink/contracts/src/v0.8/automation/AutomationCompatible.sol";
import {FunctionsRequest} from "@chainlink/contracts/src/v0.8/functions/dev/v1_0_0/libraries/FunctionsRequest.sol";

contract ChainGuardRiskOracle is
    FunctionsClient,
    AutomationCompatibleInterface
{
    struct RiskAssessment {
        uint256 riskScore; // 0-10000 (0.00% to 100.00%)
        uint256 confidence; // 0-10000 (confidence level)
        uint256 lastUpdated; // Timestamp
        string explanation; // IPFS hash of detailed explanation
        uint256[4] componentScores; // [security, financial, governance, sentiment]
    }

    // Protocol name => Risk Assessment
    mapping(string => RiskAssessment) public protocolRisks;

    // Track request IDs to protocols
    mapping(bytes32 => string) public requestIdToProtocol;

    // Chainlink Functions variables
    bytes32 public donId;
    string public riskAssessmentSource;
    uint32 public gasLimit = 300000;
    uint64 public subscriptionId;

    // Events
    event RiskAssessmentUpdated(
        string indexed protocol,
        uint256 riskScore,
        uint256 confidence,
        uint256 timestamp
    );

    event RiskAssessmentRequested(
        string indexed protocol,
        bytes32 indexed requestId
    );

    constructor(
        address functionsRouter,
        bytes32 _donId,
        uint64 _subscriptionId
    ) FunctionsClient(functionsRouter) {
        donId = _donId;
        subscriptionId = _subscriptionId;

        // Set the default JavaScript source code for ChainGuard AI integration
        riskAssessmentSource = 'const protocolName = args[0]; const apiKey = secrets.chainguardApiKey; if (!apiKey) { throw Error("ChainGuard API Key is not set in secrets."); } if (!protocolName) { throw Error("Protocol name not provided as an argument."); } const chainguardApiRequest = Functions.makeHttpRequest({ url: "https://chainguard-ai-service-xxxxxx-uc.a.run.app/assess", method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${apiKey}`, }, data: { "protocol_name": protocolName, }, timeout: 30000, }); const [response] = await Promise.all([chainguardApiRequest]); if (response.error || response.status !== 200) { throw Error(response.message || `API request failed with status ${response.status}`); } const responseData = response.data; const overallScore = responseData.risk_score.overall; const confidence = responseData.risk_score.confidence; const components = responseData.risk_score.components; const scoreAsInteger = Math.round(overallScore * 100); const confidenceAsInteger = Math.round(confidence * 10000); const securityScore = Math.round(components.protocol_security * 100); const financialScore = Math.round(components.financial_health * 100); const governanceScore = Math.round(components.governance_quality * 100); const dataQualityScore = Math.round(components.data_quality * 100); console.log(`Risk score for ${protocolName}: ${overallScore}. Returning ${scoreAsInteger} to contract.`); return Functions.encodeUint256(scoreAsInteger);';
    }

    /**
     * @dev Set the Javascript source code for risk assessment
     */
    function setRiskAssessmentSource(string memory _source) external {
        riskAssessmentSource = _source;
    }

    /**
     * @dev Request risk assessment for a protocol
     * This function triggers a Chainlink Functions request to fetch and analyze
     * risk data for a specific DeFi protocol from the Arix AI service
     */
    function requestRiskAssessment(
        string memory protocol
    ) external returns (bytes32) {
        // Build the Functions request
        FunctionsRequest.Request memory req;
        req.codeLocation = FunctionsRequest.Location.Inline;
        req.source = riskAssessmentSource;

        // Set arguments (protocol name)
        string[] memory args = new string[](1);
        args[0] = protocol;
        req.args = args;

        // Send the request
        bytes32 requestId = _sendRequest(
            FunctionsRequest.encodeCBOR(req),
            subscriptionId,
            gasLimit,
            donId
        );

        // Track which protocol this request is for
        requestIdToProtocol[requestId] = protocol;

        emit RiskAssessmentRequested(protocol, requestId);
        return requestId;
    }

    /**
     * @dev Chainlink Functions callback
     * Receives the risk assessment from Arix AI service
     */
    function fulfillRequest(
        bytes32 requestId,
        bytes memory response,
        bytes memory err
    ) internal override {
        if (err.length > 0) {
            // Handle error - could emit an event here
            return;
        }

        // Get the protocol name for this request
        string memory protocol = requestIdToProtocol[requestId];
        require(bytes(protocol).length > 0, "Unknown request ID");

        // Decode response - this will be the risk score as uint256
        uint256 riskScore = abi.decode(response, (uint256));

        // Create a new risk assessment
        RiskAssessment memory assessment;
        assessment.riskScore = riskScore; // Already scaled by 100 (e.g., 2850 for 28.5%)
        assessment.confidence = 9200; // Default confidence level (92%)
        assessment.lastUpdated = block.timestamp;
        assessment.explanation = ""; // Could be stored as IPFS hash in future
        assessment.componentScores = [1500, 2500, 4000, 9500]; // Default component scores

        // Store the assessment
        protocolRisks[protocol] = assessment;

        // Clean up the request tracking
        delete requestIdToProtocol[requestId];

        emit RiskAssessmentUpdated(
            protocol,
            assessment.riskScore,
            assessment.confidence,
            assessment.lastUpdated
        );
    }

    /**
     * @dev Chainlink Automation - Check if upkeep is needed
     */
    function checkUpkeep(
        bytes calldata
    )
        external
        view
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        // Check if any protocols need risk updates
        // Implementation would check timestamps and determine which protocols to update
        upkeepNeeded = true; // Simplified
        performData = bytes(""); // Would contain protocols to update
    }

    /**
     * @dev Chainlink Automation - Perform upkeep
     */
    function performUpkeep(bytes calldata performData) external override {
        // Trigger risk assessment updates for stale data
        // Implementation would parse performData and call requestRiskAssessment
    }

    /**
     * @dev Get current risk score for a protocol
     */
    function getRiskScore(
        string memory protocol
    ) external view returns (uint256, uint256, uint256) {
        RiskAssessment memory assessment = protocolRisks[protocol];
        return (
            assessment.riskScore,
            assessment.confidence,
            assessment.lastUpdated
        );
    }

    /**
     * @dev Get detailed risk breakdown
     */
    function getRiskBreakdown(
        string memory protocol
    )
        external
        view
        returns (
            uint256 riskScore,
            uint256 confidence,
            uint256[4] memory componentScores,
            string memory explanation
        )
    {
        RiskAssessment memory assessment = protocolRisks[protocol];
        return (
            assessment.riskScore,
            assessment.confidence,
            assessment.componentScores,
            assessment.explanation
        );
    }
}
