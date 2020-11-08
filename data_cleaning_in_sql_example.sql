drop table if exists  sunrise_spoke.campaign_title_separated;
create table sunrise_spoke.campaign_title_separated distkey(id)  as

with clean as(
  select 
  	camp.id,
  	camp.title,
  	camp.created_at::date,
  	case 
  		when camp.id = 2890 then 'c4_masscall_2020-10-20_New Hubs Mass Call Recruitment'
  		when camp.id = 2823 then 'IE_Fieldandhubs_2020-10-19_2020_Welcome Call Followup'
  		when camp.id = 2778 then 'IE_Fieldandhubs_2020-10-18_2020 HS Takover Reminder Text'
  		else title::varchar end as clean_title
  
  from sunrise_spoke.campaign camp
  ),

base as (
  select
    id,
    clean_title as title,
    split_part(clean_title, '_', 1) as designation,
    split_part(clean_title, '_', 2) as camp_tag,
    split_part(clean_title, '_', 3),
    case when id = 2410 then '2020-10-09'::date 
         when id = 2537 then '2020-10-15'::date 
         when id = 2407 then '2020-10-05'::date 
         when id = 2371 then '2020-10-05'::date
         when id = 2369 then '2010-10-04'::date 
         when id = 2372 then '2010-10-04'::date
         when id = 2372 then '2010-10-04'::date
  			 when id = 2822 then '2020-10-19'::date
         else to_date(split_part(clean_title, '_', 3), 'YYYY-MM-DD')::date end as camp_date,
    split_part(clean_title, '_', 4) as name
  	
  from clean
  where created_at > '2020-09-01' 
  and len(camp_tag) > 2 
  and 
  	(id != 1432
    and id != 1431
    and id != 1429
    and id != 1259
    and id != 1430
    and id != 1428
    and id != 1339
    and id != 1295
    and id != 2889
    and id != 2856 
    and id != 2896
    and id != 2812
    and id != 2857)
  )
  
select * from base;

grant select on sunrise_spoke.campaign_title_separated to periscope_sun
