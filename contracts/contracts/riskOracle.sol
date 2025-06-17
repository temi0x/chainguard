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
     * risk data for a specific DeFi protocol from external APIs

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
     * @dev Chainlink Functions callback - processes the response from external APIs
     * This function receives risk assessment data and updates the protocol's risk profile
     */
    function fulfillRequest(
        bytes32 requestId,
        bytes memory response,
        bytes memory err
    ) internal override {
        if (err.length > 0) {
            // Handle error - could emit an error event here
            return;
        }

        // Get the protocol name for this request
        string memory protocol = requestIdToProtocol[requestId];

        // Decode the response - expecting a structured response
        // Format: riskScore(16bits)|confidence(16bits)|security(16bits)|financial(16bits)|governance(16bits)|sentiment(16bits)
        (
            uint256 riskScore,
            uint256 confidence,
            uint256 security,
            uint256 financial,
            uint256 governance,
            uint256 sentiment,
            string memory explanation
        ) = abi.decode(
                response,
                (uint256, uint256, uint256, uint256, uint256, uint256, string)
            );

        // Update the risk assessment
        protocolRisks[protocol] = RiskAssessment({
            riskScore: riskScore,
            confidence: confidence,
            lastUpdated: block.timestamp,
            explanation: explanation,
            componentScores: [security, financial, governance, sentiment]
        });

        // Clean up the mapping
        delete requestIdToProtocol[requestId];

        emit RiskAssessmentUpdated(
            protocol,
            riskScore,
            confidence,
            block.timestamp
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
