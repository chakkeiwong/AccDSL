"""Independent expected dependency changes for the named source-view examples."""
NONE=[]
ACTOR=['actor_binding']
SOURCE=['observation_source','actor_binding']
OBS=['observation','policy','observation_source','actor_binding']
FIN=['financial','observation','policy','financial_source','observation_source','actor_binding']
CHANGES={
 'unchanged':NONE,'different_actor_same_facts':ACTOR,'unrelated_slot':NONE,
 'future_correction_old_view':NONE,'correction_available_at_boundary':OBS,
 'same_answer_new_source':SOURCE,'changed_receipt':FIN,'changed_right_family':FIN,
 'future_published':NONE,'future_ingested':NONE,'future_accepted':NONE,
 'published_but_not_accessed':NONE,'other_actor_accessed':OBS,
 'later_system_reconstructs_earlier_access':OBS,'future_economic_effect':NONE,
 'effective_boundary':OBS,'different_system_cutoff_same_heads':ACTOR,
 'different_decision_cutoff_same_heads':ACTOR,'different_effective_cutoff_same_heads':ACTOR}
