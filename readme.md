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

## 16/11/2022

create table Params_bot_Cocotier
(
    id_params_bot_cocotier int primary key auto_increment,
    api_key                text,
    secret_key             text,
    sub_account            varchar(255),
    pair_symbol            varchar(20),
    delta_hour             int,
    type_computing         enum ('n-1','n-2','n'),
    bot_id                 int,
    constraint fk_params_bot_cocotier foreign key (bot_id) references bots (bot_id) on delete cascade
);

## 17/11/2022

alter table Params_bot_Cocotier modify pair_symbol text;



