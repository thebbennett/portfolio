{% macro generate_demographics (model_name, grain=None) %}

with

-- Bring in demographic data from Contacts model
contacts as (
  select * from {{ref ('contacts')}}
),

-- Bring in the view
view as (
  select * from {{ref(model_name)}}
),

-- Gender breakdown
gender_base as (
  select
    {{ grain ~ ',' if grain}}
    contacts.gender,
    contacts.gender_summary
  from view
  left join contacts
    on view.vanid = contacts.vanid
  where
    contacts.gender ilike '%Man%'
  	or contacts.gender ilike '%male%'
    or contacts.gender ilike '%Woman%'
  	or contacts.gender ilike '%female%'
    or contacts.gender ilike '%Trans%'
    or contacts.gender ilike '%non-binary%'
    or contacts.gender ilike '%other%'

),

-- Use gender definitions to compute the number of each gender, including summaries
gender_numbers as (
  select

    {{ grain ~ ',' if grain}}

    count(*) as num_total,

    sum(case
      when gender ilike '%Woman%'
        or gender ilike '%female%'
        then 1
        else 0 end) as num_women,

    sum(case
      when (gender ilike '%Man%'
        or gender ilike '%male%')
      and gender not ilike '%Woman%'
        and gender not ilike '%female%'
        then 1
        else 0  end) as num_men,

    sum(case
      when gender ilike '%Trans%'
        then 1
        else 0  end) as num_trans,

    sum(case
      when gender ilike '%Non-binary%'
        then 1
        else 0  end) as num_nonbinary,

    sum(case
      when gender ilike '%Other%'
        then 1
        else 0  end) as num_gender_other,

    sum(case
        when gender_summary = 'Gender non-conforming'
        then 1
      else 0 end) as num_gender_non_conforming,

    sum(case
        when gender_summary = 'Cis'
        then 1
      else 0 end) as num_cis,

    sum(case
      when gender is null
        then 1
        else 0  end) as num_gender_null,

    sum(case when gender is not null
        then 1
        else 0 end) as num_with_gender,

    num_women::decimal
      / nullif(num_with_gender, 0)::decimal as pct_women,

    num_men::decimal
      / nullif(num_with_gender, 0)::decimal as pct_men,

    num_trans::decimal
      / nullif(num_with_gender, 0)::decimal as pct_trans,

    num_nonbinary::decimal
      / nullif(num_with_gender, 0)::decimal as pct_nonbinary,

    num_gender_other::decimal
      / nullif(num_with_gender, 0)::decimal as pct_gender_other,

    num_gender_non_conforming::decimal
      / nullif(num_with_gender, 0)::decimal as pct_gender_non_conforming,

    num_cis::decimal
      / nullif(num_with_gender, 0)::decimal as pct_cis,

    num_with_gender::decimal
      / nullif(num_total, 0)::decimal as pct_with_gender,

    num_gender_null::decimal
      / nullif(num_total, 0)::decimal as pct_null_gender

  from gender_base

  {% if grain %}group by 1{% endif %}
),

-- Race breakdown
race_base as (
  select
    {{ grain ~ ',' if grain}}
    contacts.race,
    contacts.race_summary
  from view
  left join contacts
    on view.vanid = contacts.vanid
),

-- Use race definitions to compute the number of each race, including summaries
race_numbers as (
  select

    {{ grain ~ ',' if grain}}

    count(*) as num_total,

    sum(case
      when race_summary = 'white'
        then 1
        else 0 end) as num_non_bipoc,

    sum(case
      when race_summary = 'BIPOC'
        then 1
        else 0 end) as num_bipoc,

    sum(case
      when race ilike '%Caucasian/White%'
        then 1
        else 0 end) as num_white,

    sum(case
      when race ilike '%Black/African American%'
        then 1
        else 0 end) as num_black,

    sum(case
      when race ilike '%Asian/Asian American%'
        then 1
        else 0 end) as num_asian,

    sum(case
      when race ilike '%Latino/Latina/Latinx%'
        then 1
        else 0 end) as num_latinx,

    sum(case
      when race ilike '%Middle Eastern%'
        then 1
        else 0 end) as num_middle_eastern,

    sum(case
      when race ilike '%Native American/First Nations/Alaska Native%'
        then 1
        else 0 end) as num_native,

    sum(case
      when race ilike '%Native Hawaiian%'
        then 1
        else 0 end) as num_native_hawaiian,

    sum(case
      when race ilike '%Pacific Islander%'
        then 1
        else 0  end) as num_pacific_islander,

    sum(case
      when race ilike '%Other%'
        then 1
        else 0 end) as num_race_other,

    sum(case
      when race is null
        then 1
        else 0 end) as num_race_null,

    sum(case when race is not null
        then 1
        else 0 end) as num_with_race,

    num_non_bipoc::decimal
      / nullif(num_with_race, 0)::decimal as pct_non_bipoc,

    num_bipoc::decimal
      / nullif(num_with_race, 0)::decimal as pct_bipoc,

    num_white::decimal
        / nullif(num_with_race, 0)::decimal as pct_white,

    num_black::decimal
      / nullif(num_with_race, 0)::decimal as pct_black,

    num_asian::decimal
      / nullif(num_with_race, 0)::decimal as pct_asian,

    num_latinx::decimal
      / nullif(num_with_race, 0)::decimal as pct_latinx,

    num_middle_eastern::decimal
      / nullif(num_with_race, 0)::decimal as pct_middle_eastern,

    num_native::decimal
      / nullif(num_with_race, 0)::decimal as pct_native,

    num_native_hawaiian::decimal
      / nullif(num_with_race, 0)::decimal as pct_native_hawaiin,

    num_pacific_islander::decimal
      / nullif(num_with_race, 0)::decimal as pct_pacific_islander,

    num_race_other::decimal
      / nullif(num_with_race, 0)::decimal as pct_race_other,

    num_with_race::decimal
      / nullif(num_total, 0)::decimal as pct_with_race,

    num_race_null::decimal
      / nullif(num_total, 0)::decimal as pct_null_race

  from race_base
  {% if grain %}group by 1{% endif %}
),


-- Class breakdown

class_base as (
  select
    {{ grain ~ ',' if grain}}
    contacts.class,
    contacts.class_summary
  from view
  left join contacts
    on view.vanid = contacts.vanid
),

class_numbers as (
  select

    {{ grain ~ ',' if grain}}

    count(*) as num_total,

    sum(case
        when class_summary = 'Working class'
          then 1
          else 0 end) as num_working_class_summary,

    sum(case
        when class_summary = 'Not working class'
          then 1
          else 0 end) as num_not_working_class_summary,

    sum(case
        when class = 'Poor and working-poor'
          then 1
          else 0 end) as num_poor,

    sum(case
        when class = 'Working-class'
          then 1
          else 0 end) as num_working_class,

    sum(case
        when class = 'Middle-class'
          then 1
          else 0 end) as num_middle_class,

    sum(case
        when class = 'Professional/managerial-class'
        then 1
        else 0 end) as num_professional_class,

    sum(case
        when class = 'Upper/owning-class'
          then 1
          else 0 end) as num_upper_class,

    sum(case
        when class is null
          or class ='N/A'
          then 1
          else 0 end) as num_class_null,

    sum(case
        when class is not null
          and  class != 'N/A'
          then 1
          else 0 end) as num_with_class,

    num_working_class_summary::decimal
      / nullif(num_with_class, 0)::decimal as pct_working_class_summary,

    num_not_working_class_summary::decimal
      / nullif(num_with_class, 0)::decimal as pct_not_working_class_summary,

    num_poor::decimal
      / nullif(num_with_class, 0)::decimal as pct_poor,

    num_working_class::decimal
      / nullif(num_with_class, 0)::decimal as pct_working_class,

    num_middle_class::decimal
      / nullif(num_with_class, 0)::decimal as pct_middle_class,

    num_professional_class::decimal
      / nullif(num_with_class, 0)::decimal as pct_professional_class,

    num_upper_class::decimal
      / nullif(num_with_class, 0)::decimal as pct_upper_class,

    num_with_class::decimal
      / nullif(num_total, 0)::decimal as pct_with_class,

    num_class_null::decimal
      / nullif(num_total, 0)::decimal as pct_class_null

  from class_base
  {% if grain %}group by 1{% endif %}

),


join_all as (
  select
    {% if grain %}race_numbers.{{grain}},{% endif %}
    race_numbers.num_total,
    --Class numbers
    num_working_class_summary,
    pct_working_class_summary,
    num_not_working_class_summary,
    pct_not_working_class_summary,
    num_poor,
    pct_poor,
    num_working_class,
    pct_working_class,
    num_middle_class,
    pct_middle_class,
    num_professional_class,
    pct_professional_class,
    num_upper_class,
    pct_upper_class,
    num_class_null,
    pct_class_null,
    num_with_class,
    pct_with_class,
    -- Race numbers
    num_non_bipoc,
    pct_non_bipoc,
    num_bipoc,
    pct_bipoc,
    num_white,
    pct_white,
    num_black,
    pct_black,
    num_asian,
    pct_asian,
    num_latinx,
    pct_latinx,
    num_middle_eastern,
    pct_middle_eastern,
    num_native,
    pct_native,
    num_native_hawaiian,
    pct_native_hawaiin,
    num_pacific_islander,
    pct_pacific_islander,
    num_race_other,
    pct_race_other,
    num_race_null,
    pct_null_race,
    num_with_race,
    pct_with_race,
    -- Gender numbers
    num_women,
    pct_women,
    num_men,
    pct_men,
    num_trans,
    pct_trans,
    num_nonbinary,
    pct_nonbinary,
    num_gender_other,
    pct_gender_other,
    num_gender_non_conforming,
    pct_gender_non_conforming,
    num_cis,
    pct_cis,
    num_gender_null,
    pct_null_gender,
    num_with_gender,
    pct_with_gender

  from class_numbers
  {% if grain %}
  left join race_numbers using({{grain}})
  left join gender_numbers using({{grain}})
  {% else %}
  cross join race_numbers
  cross join gender_numbers
  {% endif %}

)

select * from join_all

{% endmacro %}
