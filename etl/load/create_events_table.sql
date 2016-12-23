DROP TABLE IF EXISTS raw.events;

CREATE TABLE raw.events(
    EventID  VARCHAR(8000),
    Date  VARCHAR(8000),
    Year  VARCHAR(8000),
    Month  VARCHAR(8000),
    Day  VARCHAR(8000),
    SourceActorFull  VARCHAR(8000),
    SourceActorEntity  VARCHAR(8000),
    SourceActorRole  VARCHAR(8000),
    SourceActorAttribute  VARCHAR(8000),
    TargetActorFul  VARCHAR(8000),
    TargetActorEntity  VARCHAR(8000),
    TargetActorRole  VARCHAR(8000),
    TargetActorAttribute  VARCHAR(8000),
    EventCode  VARCHAR(8000),
    EventRootCode  VARCHAR(8000),
    PentaClass  VARCHAR(8000),
    GoldsteinScore  VARCHAR(8000),
    Issues  VARCHAR(8000),
    Lat  VARCHAR(8000),
    Lon  VARCHAR(8000),
    LocationName  VARCHAR(8000),
    StateName  VARCHAR(8000),
    CountryCode  VARCHAR(8000),
    SentenceID  VARCHAR(8000),
    URLs  VARCHAR(8000),
    NewsSources VARCHAR(8000)
)
;