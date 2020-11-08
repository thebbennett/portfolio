with base  as (
    SELECT
      events.title , 
        case 
            when title ilike '%Hoadley%' then 'Hoadley'  
            when title ilike '%Doglio%' then 'Doglio'  
            when title ilike '%Oliver%' then 'Oliver'  
            when title ilike '%Siegel%' then 'Siegel'  
            when title ilike '%Rashid%' then 'Rashid'  
            when title ilike '%Swearengin%' then 'Swearengin' 
            when title ilike '%Kunkel%' then 'Kunkel' 
            when title ilike '%Denney%' then 'Denney' 
            when title ilike '%Bradshaw%' then 'Bradshaw' else null end as title_adj,
        convert_timezone(events.timezone, timeslots.start_date::timestamp) as start_date ,
        timeslots.end_date , 
        part.user__given_name , 
        part.user__family_name , 
        part.user__email_address  ,
        case 
            when title ilike '%Hoadley%' then 30
            when title ilike '%Doglio%' then 40
            when title ilike '%Oliver%' then 40
            when title ilike '%Siegel%' then 72  
            when title ilike '%Rashid%' then 34
            when title ilike '%Swearengin%' then 40
            when title ilike '%Kunkel%' then 40
            when title ilike '%Denney%' then 40
            when title ilike '%Bradshaw%' then 40 else null end as shift_goal,
        case 
            when creator__email_address ilike '%XXXXXXX.org%' then 'centralized' 
            when creator__email_address ilike '%YYYYYYYY@gmail.com%' then 'centralized' 
            when creator__email_address ilike '%ZZZZZZZZZ@gmail.com%' then 'centralized' 
            when creator__email_address ilike '%AAAAAAAAA@gmail.com%' then 'centralized' 
        else 'hub' end as eventtype,

      row_number() over (partition by part.id order by part.created_date::date desc) = 1 as is_most_recent

    from  
        sunrise2020_mobilize.participations part
    left join 
        sunrise2020_mobilize.events events on part.event_id = events.id
    left join 
        sunrise2020_mobilize.timeslots timeslots on timeslots.id = part.timeslot_id 

    where 
        date_part(w, timeslots.start_date::date) = date_part(w, getdate()::date ) 
            and (events.title ilike '%Rashid%'
            or events.title ilike '%Hoadley%'
            or events.title ilike '%Swearengin%'
            or events.title ilike '%Bradshaw%'
            or events.title ilike '%Oliver%'
            or events.title ilike '%Kunkel%'
            or events.title ilike '%Denney%'
            or events.title ilike '%Doglio%'
            or events.title ilike '%Siegel%')
            and eventtype ilike 'centralized'
), de_dup as (
    select 
        title_adj , 
        shift_goal ,
        start_date ,
        end_date , 
        user__given_name , 
        user__family_name , 
        user__email_address   
    from base 
    where is_most_recent

),  by_event as (
     select 
        title_adj ||' '|| case when extract(hour from start_date) > 12 then to_char(start_date, 'Day Mon DD HH:MI AM')
            else to_char(start_date, 'Day Mon DD HH:MI PM')
            end as title_date, 
        shift_goal - count(user__email_address) as remaining,
        count(user__email_address) as num_sign_ups,   
        start_date, 
        shift_goal

      from de_dup
      group by 
        title_adj,  
        start_date,     
        shift_goal
) 

select 
    title_date,
    num_sign_ups,
    case when remaining >0 then remaining else 0 end as remainder

from 
    by_event

order by 
    start_date::date asc
