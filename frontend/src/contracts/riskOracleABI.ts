export const riskOracleABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "functionsRouter",
                "type": "address"
            },
            {
                "internalType": "bytes32",
                "name": "_donId",
                "type": "bytes32"
            },
            {
                "internalType": "uint64",
                "name": "_subscriptionId",
                "type": "uint64"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "string",
                "name": "protocol",
                "type": "string"
            },
            {
                "indexed": true,
                "internalType": "bytes32",
                "name": "requestId",
                "type": "bytes32"
            }
        ],
        "name": "RiskAssessmentRequested",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "string",
                "name": "protocol",
                "type": "string"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "riskScore",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "confidence",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "name": "RiskAssessmentUpdated",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "donId",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "gasLimit",
        "outputs": [
            {
                "internalType": "uint32",
                "name": "",
                "type": "uint32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "protocol",
                "type": "string"
            }
        ],
        "name": "getRiskBreakdown",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "riskScore",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "confidence",
                "type": "uint256"
            },
            {
                "internalType": "uint256[4]",
                "name": "componentScores",
                "type": "uint256[4]"
            },
            {
                "internalType": "string",
                "name": "explanation",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "protocol",
                "type": "string"
            }
        ],
        "name": "getRiskScore",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "name": "protocolRisks",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "riskScore",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "confidence",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "lastUpdated",
                "type": "uint256"
            },
            {
                "internalType": "string",
                "name": "explanation",
                "type": "string"
            },
            {
                "internalType": "uint256[4]",
                "name": "componentScores",
                "type": "uint256[4]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "name": "requestIdToProtocol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "protocol",
                "type": "string"
            }
        ],
        "name": "requestRiskAssessment",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "riskAssessmentSource",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_source",
                "type": "string"
            }
        ],
        "name": "setRiskAssessmentSource",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "subscriptionId",
        "outputs": [
            {
                "internalType": "uint64",
                "name": "",
                "type": "uint64"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
] as const; 