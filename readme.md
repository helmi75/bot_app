## Streamlit project 


This project is dedicated to the management of robots in decentralized finance. 



Add thess mysql commands

create table settings (
    id_setting int primary key ,
    name_setting varchar(50),
    value_setting_boolean bool,
    value_setting varchar(100)
);

insert into settings values (1,'maintenance',false,null);

alter table get_balence add crypto_wallet_pourcentage double ;

alter table get_balence modify crypto_wallet double ;






p
