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
	assert isDelegate_ <=> delegatedBy_ == account, "Violated: $x is a delegate of $account iff $x got a delegate role from ${account}. But x has a delegate role: ${isDelegate_} while delegated by ${delegatedBy_}";
}

rule delegations_in_sync_and_exclusive(method f, address delegatedTo) {
	// TODO: What if delegatedTo is 0?
	env ePre;
	address delegatingAccount = sinvoke delegations(ePre,delegatedTo); // an account that delegates one of the roles to delegatedTo

	require sinvoke _exists(ePre,delegatingAccount); // delegatingAccount must be an account
	
	address _aRewardsDelegate = sinvoke _rewardsDelegate(ePre,delegatingAccount);
	address _aVotingDelegate = sinvoke _votingDelegate(ePre,delegatingAccount);
	address _aValidatingDelegate = sinvoke _validatingDelegate(ePre,delegatingAccount);

	bool _aRewardsDelegateTo = _aRewardsDelegate == delegatedTo;
	bool _aVotingDelegateTo = _aVotingDelegate == delegatedTo;
	bool _aValidatingDelegateTo = _aValidatingDelegate == delegatedTo;
	
	require _aRewardsDelegateTo || _aVotingDelegateTo || _aValidatingDelegateTo; // at least one of the roles must be delegated to delegatedTo
	require _aRewardsDelegateTo => (!_aVotingDelegateTo && !_aValidatingDelegateTo)
			&& _aVotingDelegateTo => (!_aRewardsDelegateTo && !_aValidatingDelegateTo)
			&& _aValidatingDelegateTo => (!_aRewardsDelegateTo && !_aVotingDelegateTo); // at most one of the three roles is delegated to delegatedTo
			
	env eF;
	calldataarg arg;	
	invoke f(eF,arg);
	
	env ePost;
	address aRewardsDelegate_ = sinvoke _rewardsDelegate(ePre,delegatingAccount);
	address aVotingDelegate_ = sinvoke _votingDelegate(ePre,delegatingAccount);
	address aValidatingDelegate_ = sinvoke _validatingDelegate(ePre,delegatingAccount);

	bool aRewardsDelegateTo_ = aRewardsDelegate_ == delegatedTo;
	bool aVotingDelegateTo_ = aVotingDelegate_ == delegatedTo;
	bool aValidatingDelegateTo_ = aValidatingDelegate_ == delegatedTo;

	assert aRewardsDelegateTo_ || aVotingDelegateTo_ || aValidatingDelegateTo_, "at least one of the roles must be delegated to $delegatedTo";
	assert aRewardsDelegateTo_ => (!aVotingDelegateTo_ && !aValidatingDelegateTo_)
			&& aVotingDelegateTo_ => (!aRewardsDelegateTo_ && !aValidatingDelegateTo_)
			&& aValidatingDelegateTo_ => (!aRewardsDelegateTo_ && !aVotingDelegateTo_), "at most one of the three roles is delegated to $delegatedTo";
} 

rule functional_get_account_from_voter_result(address account) {
	// TODO: What if voting delegate is 0?
	// If an account has a voting delegate, getAccountFromVoter(delegate) must return that account
	
	env e;
		
	address votingDelegate = sinvoke _votingDelegate(e, account);
	// assume the invariant on delegations
	require sinvoke delegations(e, votingDelegate) == account;
	
	env eF;
	address gotAccountFromVoterResult = sinvoke getAccountFromVoter(eF, votingDelegate);
	
	assert votingDelegate != 0 => gotAccountFromVoterResult == account, "Account $account has a voting delegate $votingDelegate but getAccountFromVoter($votingDelegate) returns $gotAccountFromVoterResult instead of account";
	
	assert votingDelegate == 0 => gotAccountFromVoterResult == account, "Account $account does not have a voting delegate but getAccountFromVoter($votingDelegate) returns $gotAccountFromVoterResult";
}

rule functional_get_account_from_voter_success(address account, address delegate) {
	// TODO: What if voting delegate is 0?
	// getAccountFromVoter(address) must fail if “address” is not an account or voting delegate
	env e;
	
	// get an accounts voting delegate
	address votingDelegate = sinvoke _votingDelegate(e, account);
	// assume the invariant on delegations
	require sinvoke delegations(e, votingDelegate) == account;
	
	bool isDelegate = delegate == votingDelegate;
	bool isAccount = sinvoke _exists(e, delegate);
	
	env eF;
	require eF.msg.value == 0;
	address gotAccountFromVoterResult = invoke getAccountFromVoter(eF, delegate);
	bool success = !lastReverted;
	
	assert (!isDelegate && !isAccount) => !success, "getAccountFromVoter($delegate) must fail if $delegate is not an account (isAccount=${isAccount}) nor a voting delegate (isDelegate=${isDelegate})";
}

// TODO Repeat for validating delegate, rewards delegate:
/*
- If an account has a validating delegate, getAccountFromValidator(delegate) must return that account
- getAccountFromValidator(address) must fail if “address” is not an account or validating delegate
- If an account has a rewards delegate, getAccountFromRewardsRecipient(delegate) must return that account
- getAccountFromRewardsRecipient(address) must fail if “address” is not an account or rewards delegate
 */

rule modifying_deposits(address a, uint256 someNoticePeriod, uint256 someAvailabilityTime, method f) {
	// just mapping out functions that affect an account's deposits
	env _e;
	uint256 _lenNoticePeriodsValue = sinvoke _lenNoticePeriods(_e,a);
	uint256 _lenAvailabilityTimesValue = sinvoke _lenAvailabilityTimes(_e,a);
	uint256 _someBondedValue; uint256 _someBondedIndex;
	_someBondedValue, _someBondedIndex = sinvoke getBondedDeposit(_e,a,someNoticePeriod);
	uint256 _someNotifiedValue; uint256 _someNotifiedIndex;
	_someNotifiedValue, _someNotifiedIndex = sinvoke getNotifiedDeposit(_e,a,someAvailabilityTime);
	
	env eF;
	calldataarg arg;
	invoke f(eF,arg);
	
	env e_;
	uint256 lenNoticePeriodsValue_ = sinvoke _lenNoticePeriods(e_,a);
	uint256 lenAvailabilityTimesValue_ = sinvoke _lenAvailabilityTimes(e_,a);
	uint256 someBondedValue_; uint256 someBondedIndex_;
	someBondedValue_, someBondedIndex_ = sinvoke getBondedDeposit(e_,a,someNoticePeriod);
	uint256 someNotifiedValue_; uint256 someNotifiedIndex_;
	someNotifiedValue_, someNotifiedIndex_ = sinvoke getNotifiedDeposit(e_,a,someAvailabilityTime);
	
	assert _lenNoticePeriods == lenNoticePeriodsValue_, "Method changed length of notice periods";
	assert _lenAvailabilityTimesValue == lenAvailabilityTimesValue_, "Method changed length of availability times";
	assert _someBondedValue == someBondedValue_, "Method changed a bonded value";
	assert _someBondedIndex == someBondedIndex_, "Method changed a bonded index";
	assert _someNotifiedValue == someNotifiedValue_, "Method changed a notified value";
	assert _someNotifiedIndex == someNotifiedIndex_, "Method changed a notified index";
}

rule valid_notice_period_for_deposit(address a, uint256 someNoticePeriod, method f) {
	// An account should not be able to deposit with a notice period > the current max notice period
	env _e;
	uint256 _maxNoticePeriodValue = sinvoke maxNoticePeriod(_e);
	
	uint256 _someBondedValue; uint256 _someBondedIndex;
	_someBondedValue, _someBondedIndex = sinvoke getBondedDeposit(_e,a,someNoticePeriod);
	require someNoticePeriod > _maxNoticePeriodValue => (_someBondedValue == 0 && _someBondedIndex == 0);
	
	env eF;
	calldataarg arg;
	invoke f(eF,arg);
	
	env e_;
	uint256 maxNoticePeriodValue_ = sinvoke maxNoticePeriod(e_);
	
	uint256 someBondedValue_; uint256 someBondedIndex_;
	someBondedValue_, someBondedIndex_ = sinvoke getBondedDeposit(e_,a,someNoticePeriod);
	
	assert someNoticePeriod > maxNoticePeriodValue_ => (someBondedValue_ == 0 && someBondedIndex_ == 0);
}

rule cant_notify_an_unbonded_deposit(address a, uint256 someNoticePeriod, method f) {
	// availability time for someNoticePeriod will be eF.block.timestamp+someNoticePeriod;
	env _e;
	env eF;
	env e_;
	
	uint256 matchingAvailabilityTime = eF.block.timestamp+someNoticePeriod; // availability time is notify time + notice period set beforehand
	
	uint256 _someBondedValue; uint256 _someBondedIndex;
	_someBondedValue, _someBondedIndex = sinvoke getBondedDeposit(_e,a,someNoticePeriod);
	uint256 _someNotifiedValue; uint256 _someNotifiedIndex;
	_someNotifiedValue, _someNotifiedIndex = sinvoke getNotifiedDeposit(_e,a,matchingAvailabilityTime);
	
	// not notified before:
	require _someNotifiedValue == 0 && _someNotifiedIndex == 0;
	
	calldataarg arg;
	invoke f(eF,arg);
	
	uint256 someBondedValue_; uint256 someBondedIndex_;
	someBondedValue_, someBondedIndex_ = sinvoke getBondedDeposit(e_,a,someNoticePeriod);
	uint256 someNotifiedValue_; uint256 someNotifiedIndex_;
	someNotifiedValue_, someNotifiedIndex_ = sinvoke getNotifiedDeposit(e_,a,matchingAvailabilityTime);
	
	// if now we notified, necessarily, it was bonded BEFORE
	assert (someNotifiedValue_ != 0 || someNotifiedIndex_ != 0) => (_someBondedValue != 0 || _someBondedIndex != 0), "Violated: An account should never be able to notify a deposit which hadnt previously been deposited";
}

rule modifying_weight(address a, uint256 someNoticePeriod, uint256 someAvailabilityTime, method f) {
	// just mapping out functions that affect an account's weight
	env _e;
	uint256 _accountWeight = sinvoke _weight(_e,a);
	
	env eF;
	calldataarg arg;
	invoke f(eF,arg);
	
	env e_;
	uint256 accountWeight_ = sinvoke _weight(e_,a);
	
	assert _accountWeight == accountWeight_, "Method changed weight of account";
}

rule atomic_deposit_notification(uint256 someNoticePeriod, uint256 notifyValue) {
	// Notifying a deposit should always reduce the balance of a bonded deposit by the same amount that it increments the balance of a notified deposit
	env _e;
	env eF;
	env e_;
	
	address a = eF.msg.sender; // our account will execute notify()
	uint256 matchingAvailabilityTime = eF.block.timestamp+someNoticePeriod; // availability time is notify time + notice period set beforehand
	
	uint256 _someBondedValue; uint256 _someBondedIndex;
	_someBondedValue, _someBondedIndex = sinvoke getBondedDeposit(_e,a,someNoticePeriod);
	uint256 _someNotifiedValue; uint256 _someNotifiedIndex;
	_someNotifiedValue, _someNotifiedIndex = sinvoke getNotifiedDeposit(_e,a,matchingAvailabilityTime);
	
	invoke notify(eF, notifyValue, someNoticePeriod);
	
	uint256 someBondedValue_; uint256 someBondedIndex_;
	someBondedValue_, someBondedIndex_ = sinvoke getBondedDeposit(e_,a,someNoticePeriod);
	uint256 someNotifiedValue_; uint256 someNotifiedIndex_;
	someNotifiedValue_, someNotifiedIndex_ = sinvoke getNotifiedDeposit(e_,a,matchingAvailabilityTime);
	
	// some notified value should increase, some bonded value should decrease
	assert someNotifiedValue_ - _someNotifiedValue == _someBondedValue - someBondedValue_, "Violated: Difference between new and old bonded value should be the same as difference of old and new notified value";
	
	assert someNotifiedValue_ - _someNotifiedValue == notifyValue
			&& _someBondedValue - someBondedValue_ == notifyValue, "Violated: When notify succeeds, difference between old and new bonded value is the notify value $notifyValue";
}

rule cant_rebond_non_notified(uint256 rebondValue, uint256 depositAvailabilityTime) {
	// An account should never be able to rebond a non-notified deposit
	env _e;
	env eF;
	
	invoke rebond(eF, rebondValue, depositAvailabilityTime);
	assert false, "placeholder";
}

// TODO: deleteElement should always be called with lastIndex == list.length-1 - check using assertion in the code and assert mode?
