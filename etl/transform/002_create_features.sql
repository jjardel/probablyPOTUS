-- possible featues for identifying crazy Trump tweets:
  -- android/iphone
  -- number of retweets X
  -- number of likes X
  -- ratio of retweets/likes X
  -- number of exclamation points X
  -- number of capitalized substrings X
  -- is_tweetstorm?

DROP TABLE IF EXISTS clean.crazy_tweet_features;

CREATE TABLE clean.crazy_tweet_features AS
WITH c1 AS(
    SELECT *,
        created_at AS dummy
    FROM clean.tweets
    WHERE user_screen_name = 'realDonaldTrump'
),
c2 AS(
    SELECT
        created_at,
        favorites,
        followers,
        id_str,
        num_statuses,
        quoted_status_id_str,
        quoted_status_text,
        retweets,
        text,
        tweet_source,
        user_id_str,
        user_name,
        user_screen_name,
        COALESCE(retweets::FLOAT / NULLIF(favorites::FLOAT, 0), 0) AS retweets_to_faves,
        array_length(string_to_array(text, '!'), 1) - 1 AS num_exclamation_points,
        length(text) AS num_characters,
        array_length(regexp_split_to_array(text, '([A-Z][\w-]*(\s+[A-Z][\w-]*)+)'), 1) - 1 AS num_uppercase_strings,
        CASE WHEN text LIKE '"@%' OR text LIKE 'RT%' THEN 1 ELSE 0 END AS is_trump_retweet,   -- he often RTs lots of tweets in a row, and starts by copying the text of the tweet
        LAG(created_at, 1) OVER w AS timestamp_last_tweet,
        LEAD(created_at, 1) OVER w AS timestamp_next_tweet
    FROM c1
    WHERE user_screen_name = 'realDonaldTrump'
    WINDOW w AS (ORDER BY dummy)
)
SELECT
    created_at,
    favorites,
    followers,
    id_str,
    num_statuses,
    quoted_status_id_str,
    quoted_status_text,
    retweets,
    text,
    tweet_source,
    user_id_str,
    user_name,
    user_screen_name,
    retweets_to_faves,
    num_exclamation_points,
    num_characters,
    num_uppercase_strings,
    is_trump_retweet,
    CASE WHEN (created_at - timestamp_last_tweet < '10 minutes' OR timestamp_next_tweet - created_at < '10 minutes')
              AND tweet_source = 'android' -- these are likely tweets coming from his device
              AND is_trump_retweet != 1
              THEN 1 ELSE 0 END AS is_tweetstorm

FROM c2;


