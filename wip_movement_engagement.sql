with 

online_actions_history as (
  
  select
  contacts_forms.vanid,
  forms.onlineformname as action_name,
  t.onlineformtypename as action_type,
  CONVERT_TIMEZONE ('UTC', 'America/New_York', contacts_forms.datecreated::timestamp) as action_date
  
  from sunrise_ea.tsm_tmc_contactsonlineforms_sm contacts_forms 
  left join sunrise_ea.tsm_tmc_onlineforms_sm forms 
    on contacts_forms.onlineformid = forms.onlineformid
  left join tmc_van.tsm_tmc_onlineformtypes t
	  on forms.onlineformtypeid = t.onlineformtypeid
  
  where t.onlineformtypename not ilike 'Event Signup Form' 

), digital_aquisition_history as (
  
  select
    contacts_forms.vanid,
    forms.onlineformname as action_name,
    'Digital Acquisition' as action_type,
    CONVERT_TIMEZONE ('UTC', 'America/New_York', contacts_forms.datecreated::timestamp) as action_date
  
  from sunrise_ea.tsm_tmc_contactsonlineforms_sm contacts_forms 
  left join sunrise_ea.tsm_tmc_onlineforms_sm forms 
    on contacts_forms.onlineformid = forms.onlineformid
  left join tmc_van.tsm_tmc_onlineformtypes t
	  on forms.onlineformtypeid = t.onlineformtypeid
  
  where action_name ilike '%Facebook Lead Gen Form%'
      or action_name ilike '% Ads %'
      or action_name ilike '%_Ads_%'
      or action_name ilike 'Squarespace --> EveryAction Zapier Form'
      or action_name ilike 'DO NOT USE - Website Sign Up - Home'
      or action_name ilike 'Wordpress Website Signup Form'
      or action_name ilike 'DO NOT USE - Wordpress Website Email Signup Form'
      or action_name ilike 'Slack Guest --> EveryAction Zapier Form%'
      or action_name ilike 'Shopify Signup Zapier Form'
   
), event_history as (
  
  select
  	signups.vanid,
  	events.eventname as action_name,
    case when signups.eventrolename = 'Attendee' and status.eventstatusname = 'Completed' then 'Event Attendee'
        when signups.eventrolename = 'Host' and status.eventstatusname = 'Completed' then 'Event Host' end as action_type,
  	CONVERT_TIMEZONE ('UTC', 'America/New_York', signups.datetimeoffsetbegin::timestamp) as action_date
  
  from sunrise_ea.tsm_tmc_eventsignups_sm signups 
  left join  sunrise_ea.tsm_tmc_events_sm events 
    on events.eventid = signups.eventid
  left join  sunrise_ea.tsm_tmc_eventsignupsstatuses_sm status 
    on signups.eventsignupid = status.eventsignupid
  
  where status.eventstatusname ilike 'completed'
  
), national_volunteers as (
  
  select 
    codes.vanid,
    ac.activistcodename::varchar as action_name,
    case when ac.activistcodename ilike 'MST%' then 'National Volunteer'
         when ac.activistcodename ilike 'RN%' then 'Role Network' else null end as action_type,
    CONVERT_TIMEZONE ('UTC', 'America/New_York', codes.datecreated::timestamp) as action_date
    
  from sunrise_ea.tsm_tmc_contactsactivistcodes_sm codes 
  
  left join tmc_van.sun_activistcodes ac 
    on codes.activistcodeid = ac.activistcodeid
  
  where ac.activistcodename ilike 'MST%'
    or ac.activistcodename ilike 'RN%'
  
), donations as (
  
  select 
    emails.vanid,
    max(committeename||' '|| 'donation') as action_name,
    'Donation' as action_type,
    max(CONVERT_TIMEZONE ('UTC', 'America/New_York', createdat::timestamp)) as action_date
  
  from tmc_ab.sun_donations donations
  
  left join sunrise_ea.tsm_tmc_contactsemails_sm emails 
    on donations.email = emails.email 
  
  group by 1 -- group by due to EAs bad duplication 
  
  -- start with a base to remove first data import 
), email_history_base as (
    select 
    contacts.vanid,
    'Email Sign Up' as action_name,
    'Email Sign Up' as action_type,
     max(CONVERT_TIMEZONE ('UTC', 'America/New_York', sub.datecreated::timestamp)) as action_date 
      
  from sunrise_ea.tsm_tmc_emailsubscriptions_sm sub 
  left join sunrise_ea.tsm_tmc_contactsemails_sm emails
    on sub.email = emails.email 
  left join sunrise_ea.tsm_tmc_contacts_sm contacts
    on emails.vanid = contacts.vanid 
  where sub.committeeid = 80541
  	and sub.emailsubscriptionstatusid != 0
  
  group by 1 -- group by due to EAs bad duplication 
 
), email_history as (
    
    select * from email_history_base 
    where action_date::date != '2020-02-26'::date 

    
), action_history as (
    
    select * from online_actions_history
    union all 
    select * from event_history
    union all
    select * from national_volunteers
    union all 
    select * from donations
    union all 
    select * from email_history
    union all 
    select * from digital_aquisition_history

), actions_ranked as (
  
  select 
    action_history.*,
    rank() over (partition by vanid order by action_date asc) as rnk
  
  from action_history
  
) select * from actions_ranked
