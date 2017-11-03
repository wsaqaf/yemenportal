every 5.minutes do
  rake "rss_parser"
end

every 3.hours do
  rake "posts_clustering"
end
