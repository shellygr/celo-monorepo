pragma solidity ^0.5.8;

import "contracts/governance/IntegerSortedLinkedList.sol";

contract IntegerSortedListCheck {
	using IntegerSortedLinkedList for SortedLinkedList.List;
	
	SortedLinkedList.List l;
	
	function getElementLesser(uint256 k) public view returns (uint256) {
		return uint256(l.list.elements[bytes32(k)].previousKey);
	}
	
	function getElementGreater(uint256 k) public view returns (uint256) {
		//require (l.list.elements[bytes32(k)].exists);
		return uint256(l.list.elements[bytes32(k)].nextKey);
	}
	
	function getNumElements() public view returns (uint256) {
		return l.list.numElements;
	}
	
	function getTail() public view returns (uint256) {
		return uint256(l.list.tail);
	}
	
	function getHead() public view returns (uint256) {
		return uint256(l.list.head);
	}
	
	function insert(
		uint256 key,
		uint256 value,
		uint256 lesserKey,
		uint256 greaterKey
	) public {
		l.insert(key,value,lesserKey,greaterKey);
	}
	
	function remove(uint256 key) public {
		l.remove(key);
	}
	
	function update(
		uint256 key,
		uint256 value,
		uint256 lesserKey,
		uint256 greaterKey
	) public {
		l.update(key,value,lesserKey,greaterKey);
	}
	
	function contains(uint256 key) public returns (bool) {
		return l.contains(key);
	}
	
	function getValue(uint256 key) public returns (uint256) {
		return l.getValue(key);
	}
}