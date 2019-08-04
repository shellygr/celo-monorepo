pragma specify 0.1

rule account_empty_unless_created(method f, address account) {
	/* What is an "empty" account?
		We define an empty account as:
			(1) zero length notice periods, zero length availability-times
			(2) all zero Rewards
			(3) all zero Voting
			(4) all zero Validating
			(5) zero weight
			
		A non-created account has exists = false.
	 */

	env ePre;
	bool _empty1 = (sinvoke _lenNoticePeriods(ePre,account) == 0) && (sinvoke _lenAvailabilityTimes(ePre,account) == 0);
	bool _empty2 = (sinvoke _rewardsDelegate(ePre,account) == 0) && (sinvoke _rewardsLastRedeemed(ePre,account) == 0); // TODO: Add support for uint96
	bool _empty3 = (sinvoke _votingDelegate(ePre,account) == 0) && (sinvoke _votingFrozen(ePre,account) == false);
	bool _empty4 = (sinvoke _validatingDelegate(ePre,account) == 0);
	bool _empty5 = (sinvoke _weight(ePre,account) == 0);

	bool _existsAccount = sinvoke _exists(ePre,account);
	 
	require !_existsAccount => (_empty1 && _empty2 && _empty3 && _empty4 && _empty5);
	
	env eF; 
	calldataarg arg; 
	invoke f(eF,arg);
 
	env ePost;
	bool empty1_ = (sinvoke _lenNoticePeriods(ePost,account) == 0) && (sinvoke _lenAvailabilityTimes(ePost,account) == 0);
	bool empty2_ = (sinvoke _rewardsDelegate(ePost,account) == 0) && (sinvoke _rewardsLastRedeemed(ePost,account) == 0); // TODO: Add support for uint96
	bool empty3_ = (sinvoke _votingDelegate(ePost,account) == 0) && (sinvoke _votingFrozen(ePost,account) == false);
	bool empty4_ = (sinvoke _validatingDelegate(ePost,account) == 0);
	bool empty5_ = (sinvoke _weight(ePost,account) == 0);

	bool existsAccount_ = sinvoke _exists(ePost,account);
	 
	assert !existsAccount_ => (empty1_ && empty2_ && empty3_ && empty4_ && empty5_), "Violated: after invoking, an account cannot be un-created yet non-empty";
}

rule address_cant_be_both_account_and_delegate(method f, address x) {
	address account; // an account that may point to x being a delegate
	
	env ePre;
	bool _isAccount = sinvoke _exists(ePre,x); // x is an account if true
	
	bool _aExists = sinvoke _exists(ePre,account);
	address _aRewardsDelegate = sinvoke _rewardsDelegate(ePre,account);
	address _aVotingDelegate = sinvoke _votingDelegate(ePre,account);
	address _aValidatingDelegate = sinvoke _validatingDelegate(ePre,account);
	
	require _aExists; // we require account to be an account
	
	bool _isDelegate = _aRewardsDelegate == x || _aVotingDelegate == x || _aValidatingDelegate == x; // x is a delegate if true
	address _delegatedBy = sinvoke delegations(ePre,x);
	
	require !(_isDelegate && _isAccount); // x cannot be both a delegate and an account
	require _isDelegate <=> _delegatedBy == account; // x is a delegate of account iff x got a delegate role from account (see delegations_in_sync_and_exclusive)
	
	env eF; 
	calldataarg arg; 
	invoke f(eF,arg);


	env ePost;
	bool isAccount_ = sinvoke _exists(ePost,x); // x is an account if true
	
	bool aExists_ = sinvoke _exists(ePost,account);
	address aRewardsDelegate_ = sinvoke _rewardsDelegate(ePost,account);
	address aVotingDelegate_ = sinvoke _votingDelegate(ePost,account);
	address aValidatingDelegate_ = sinvoke _validatingDelegate(ePost,account);
	
	require aExists_; // we require account to still be an account
	
	bool isDelegate_ = aRewardsDelegate_ == x || aVotingDelegate_ == x || aValidatingDelegate_ == x; // x is a delegate if true
	address delegatedBy_ = sinvoke delegations(ePost,x);
	
	assert !(isDelegate_ && isAccount_),"$x cannot be both a delegate and an account";
	assert isDelegate_ <=> delegatedBy_ == account, "Violated: $x is a delegate of $account iff $x got a delegate role from ${account}. But x has a delegate role: ${isDelegate_} while delegated by ${delegatedBy}";
}

rule delegations_in_sync_and_exclusive(method f, address delegatedTo) {
	env ePre;
	address delegatingAccount = sinvoke delegations(ePre,delegatedTo); // an account that delegates one of the roles to delegatedTo

	require sinvoke _exists(ePre,delegatingAccount); // delegatingAccount must be an account
	
	address _aRewardsDelegate = sinvoke _rewardsDelegate(ePre,delegatingAccount);
	address _aVotingDelegate = sinvoke _votingDelegate(ePre,delegatingAccount);
	address _aValidatingDelegate = sinvoke _validatingDelegate(ePre,delegatingAccount);

	require _aRewardsDelegate || _aVotingDelegate || _aValidatingDelegate; // at least one of the roles must be delegated to delegatedTo
	require _aRewardsDelegate => (!_aVotingDelegate && !_aValidatingDelegate)
			&& _aVotingDelegate => (!_aRewardsDelegate && !_aValidatingDelegate)
			&& _aValidatingDelegate => (!_aRewardsDelegate && !_aVotingDelegate); // at most one of the three roles is delegated to delegatedTo
			
	env eF;
	calldataarg arg;	
	invoke f(eF,arg);
	
	env ePost;
	address aRewardsDelegate_ = sinvoke _rewardsDelegate(ePre,delegatingAccount);
	address aVotingDelegate_ = sinvoke _votingDelegate(ePre,delegatingAccount);
	address aValidatingDelegate_ = sinvoke _validatingDelegate(ePre,delegatingAccount);

	assert aRewardsDelegate_ || aVotingDelegate_ || aValidatingDelegate_, "at least one of the roles must be delegated to $delegatedTo";
	assert aRewardsDelegate_ => (!aVotingDelegate_ && !aValidatingDelegate_)
			&& aVotingDelegate_ => (!aRewardsDelegate_ && !aValidatingDelegate_)
			&& aValidatingDelegate_ => (!aRewardsDelegate_ && !aVotingDelegate_), "at most one of the three roles is delegated to $delegatedTo";
} 


// deleteElement should always be called with lastIndex == list.length-1
