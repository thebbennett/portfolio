with base_response as 
(select 
  campaign_contact_id, 
  sum(case when is_from_contact = 'f' then 1 else 0 end) as num_text_sent,
  sum(case when is_from_contact = 't' then 1 else 0 end) as num_text_received

from sunrise_spoke.message mes 
group by campaign_contact_id
)


SELECT
   camp_adj.camp_tag, 
   camp_adj.name ,
   sum(num_text_sent) as total_texts_sent,
  sum(case when qr.value like '%Yes%' then 1 else 0 end) as num_comitted,
  sum(case when cc.is_opted_out ='t' then 1 end)::decimal / count(cc.id)::decimal as opt_out_rate,

  sum(case when base_response.num_text_received > 0 and cc.is_opted_out = 'f' then 1 else 0 end)::decimal / sum(case when base_response.num_text_received >= 0 then 1 else 0 end)::decimal  as  response_rate

  from base_response
  left join sunrise_spoke.campaign_contact cc 
    on cc.id = base_response.campaign_contact_id
  left join sunrise_spoke.question_response qr 
    on qr.campaign_contact_id = cc.id
  left join sunrise_spoke.campaign_title_separated camp_adj 
    on cc.campaign_id = camp_adj.id
  left join sunrise_spoke.campaign camp 
    on cc.campaign_id = camp.id

where (camp_adj.designation ilike 'IE'
      or camp_adj.camp_tag ilike '%tripling%'
      or camp_adj.camp_tag ilike '%requestaballot%'
      or camp_adj.camp_tag ilike '%gotv%')
group by
   camp_adj.camp_tag, 
   camp_adj.name
