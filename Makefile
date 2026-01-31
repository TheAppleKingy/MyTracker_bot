DEV_COMPOSE=build/dev/compose.yaml
PROD_COMPOSE=build/prod/compose.yaml

tracker.bot.network.setup:
	@docker network create MyTrackerNetwork >/dev/null 2>&1 || true

#--------------------------------------------------------------------------------------

tracker.bot.dev.build: tracker.bot.network.setup
	@docker compose -f ${DEV_COMPOSE} build


tracker.bot.dev.start:
	@docker compose -f ${DEV_COMPOSE} up


tracker.bot.dev.build.start: tracker.bot.dev.build
	@docker compose -f ${DEV_COMPOSE} up

tracker.bot.dev.down:
	@docker compose -f ${DEV_COMPOSE} down

#--------------------------------------------------------------------------------------

tracker.bot.prod.build: tracker.bot.network.setup
	@docker compose -f ${PROD_COMPOSE} build


tracker.bot.prod.start:
	@docker compose -f ${PROD_COMPOSE} up -d


tracker.bot.prod.build.start: tracker.bot.prod.build
	@docker compose -f ${PROD_COMPOSE} up -d

tracker.bot.prod.down:
	@docker compose -f ${PROD_COMPOSE} down

