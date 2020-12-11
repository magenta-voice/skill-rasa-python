# Sample Dialog Manager

This is a Magenta voice skill interface built around [Rasa Open Source](https://rasa.com/docs/) bot.

## How it works

Skill defines two intent handlers: RASA__HANDOVER and CVI_INTERNAL_ASK_FREETEXT.

After a first invoke skill answers with ASK_FREETEXT response type and receives user's answer 
as raw STT response in CVI_INTERNAL_ASK_FREETEXT intent handler. 

The intent handler simply forwards user's answer to Rasa server and reads out its response as ASK_FREETEXT type.

## Components

The skill consists of Rasa server (serves the NLU model and provides web hooks for programmatic access) 
and the skill itself. 

#### Rasa Server

Runs on http://localhost:5005

#### Skill

Runs on standard port :4242

## Building Rasa Model

Rasa NLU models are defined in `data` folder:

- `nlu.yml`: intents training utterances 
- `rules.yml`: rule definitions
- `stories.yml`: chat stories definitions

Model configuration is defined in those `.yml` files:

- `config.yml` 
- `credentials.yml` 
- `domain.yml` 
- `endpoints.yml` 

For a quick reference about configuring and building Rasa models, 
see: https://rasa.com/docs/rasa/user-guide/rasa-tutorial/
