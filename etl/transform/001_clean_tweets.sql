DROP TABLE IF EXISTS clean.tweets;

CREATE TABLE clean.tweets AS
    SELECT
        created_at::timestamp AS created_at,
        favorite_count::INT AS favorites,
        id_str,
        quoted_status_id_str,
        quoted_status_text,
        retweet_count::INT AS retweets,

        -- group common sources
        CASE WHEN "source" ILIKE '%android%' THEN 'android'
             WHEN "source" ILIKE '%iphone%' OR "source" ILIKE '%ipad%' THEN 'iphone'
             WHEN "source" ILIKE '%twitter web client%' THEN 'web'
             WHEN "source" ILIKE '%socialflow%' THEN 'socialflow'
        ELSE 'other'
        END AS tweet_source,

        text,
        user_followers_count::INT AS followers,
        user_id_str,
        user_name,
        user_screen_name,
        user_statuses_count::INT AS num_statuses

    FROM raw.tweets;

