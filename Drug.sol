// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Drug {
    struct User {
        string username;
        bool isRegistered;
        uint256 registrationDate;
    }

    struct Product {
        string name;
        uint256 price;
        uint256 quantity;
        string description;
        string imageHash;
        uint256 lastUpdateDate;
        string currentStatus;
        address owner;
        bool exists;
    }

    struct TraceRecord {
        string productName;
        string traceType;
        string details;
        uint256 timestamp;
        address updatedBy;
    }

    mapping(address => User) public users;
    mapping(string => Product) public products;
    mapping(string => TraceRecord[]) public traceHistory;
    
    address public owner;
    
    event UserRegistered(address indexed userAddress, string username);
    event ProductAdded(string indexed name, address indexed owner);
    event TraceUpdated(string indexed productName, string traceType, uint256 timestamp);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyRegistered() {
        require(users[msg.sender].isRegistered, "User not registered");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    function registerUser(string memory username) public {
        require(!users[msg.sender].isRegistered, "User already registered");
        require(bytes(username).length > 0, "Username cannot be empty");
        
        users[msg.sender] = User({
            username: username,
            isRegistered: true,
            registrationDate: block.timestamp
        });
        
        emit UserRegistered(msg.sender, username);
    }
    
    function addProduct(
        string memory name,
        uint256 price,
        uint256 quantity,
        string memory description,
        string memory imageHash
    ) public onlyRegistered {
        require(bytes(name).length > 0, "Product name cannot be empty");
        require(!products[name].exists, "Product already exists");
        
        products[name] = Product({
            name: name,
            price: price,
            quantity: quantity,
            description: description,
            imageHash: imageHash,
            lastUpdateDate: block.timestamp,
            currentStatus: "Production",
            owner: msg.sender,
            exists: true
        });
        
        emit ProductAdded(name, msg.sender);
    }
    
    function updateTrace(
        string memory productName,
        string memory traceType,
        string memory details
    ) public onlyRegistered {
        require(products[productName].exists, "Product does not exist");
        require(bytes(traceType).length > 0, "Trace type cannot be empty");
        
        TraceRecord memory newTrace = TraceRecord({
            productName: productName,
            traceType: traceType,
            details: details,
            timestamp: block.timestamp,
            updatedBy: msg.sender
        });
        
        traceHistory[productName].push(newTrace);
        products[productName].currentStatus = traceType;
        products[productName].lastUpdateDate = block.timestamp;
        
        emit TraceUpdated(productName, traceType, block.timestamp);
    }
    
    function getProduct(string memory name) public view returns (
        string memory productName,
        uint256 price,
        uint256 quantity,
        string memory description,
        string memory imageHash,
        uint256 lastUpdateDate,
        string memory currentStatus,
        address productOwner
    ) {
        require(products[name].exists, "Product does not exist");
        Product memory product = products[name];
        return (
            product.name,
            product.price,
            product.quantity,
            product.description,
            product.imageHash,
            product.lastUpdateDate,
            product.currentStatus,
            product.owner
        );
    }
    
    function getTraceHistory(string memory productName) public view returns (
        TraceRecord[] memory
    ) {
        require(products[productName].exists, "Product does not exist");
        return traceHistory[productName];
    }
}