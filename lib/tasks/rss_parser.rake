task rss_parser: :environment do
  Source.find_each do |source|
    PostsFetcherJob.perform_later(source.id)
  end
end
