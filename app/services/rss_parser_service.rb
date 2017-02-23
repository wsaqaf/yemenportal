class RSSParserService
  def self.call
    Source.find_each do |source|
      NewsParserJob.perform_later(source.id)
    end
  end
end
