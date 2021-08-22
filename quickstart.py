from tortoise.models import Model
from tortoise import fields, Tortoise, run_async


class Tournament(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return self.name


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    # References to other models are defined in format
    # "{app_name}.{model_name}" - where {app_name} is defined in tortoise config
    tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
    participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')

    def __str__(self):
        return self.name


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name


async def run():
    await Tortoise.init(db_url="postgres://postgres:123456@127.0.0.1:5432/tortoise", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # Create instance by save
    tournament = Tournament(name='New Tournament')
    await tournament.save()

    # Or by .create()
    await Event.create(name='Without participants', tournament=tournament)
    event = await Event.create(name='Test', tournament=tournament)
    participants = []
    for i in range(2):
        team = await Team.create(name='Team {}'.format(i + 1))
        participants.append(team)

    # M2M Relationship management is quite straightforward
    # (look for methods .remove(...) and .clear())
    # 注意：这个地方演示多对多的添加/移除s
    await event.participants.add(*participants)

    # You can query related entity just with async for
    async for team in event.participants:
        pass

    # After making related query you can iterate with regular for,
    # which can be extremely convenient for using with other packages,
    # for example some kind of serializers with nested support
    for team in event.participants:
        pass

    # Or you can make preemptive call to fetch related objects,
    # so you can work with related objects immediately
    selected_events = await Event.filter(
        participants=participants[0].id
    ).prefetch_related('participants', 'tournament')
    for event in selected_events:
        print(event.tournament.name)
        print([t.name for t in event.participants])

    # Tortoise ORM supports variable depth of prefetching related entities
    # This will fetch all events for team and in those team tournament will be prefetched
    await Team.all().prefetch_related('events__tournament')

    # You can filter and order by related models too
    # await Tournament.filter(
    #     events__name__in=['Test', 'Prod']
    # ).order_by('-events__participants__name').distinct()

if __name__ == "__main__":
    run_async(run())

