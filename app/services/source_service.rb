class SourceService
  FACEBOOK_REGEXP = %r{www\.facebook\.com\/}

  def self.source_type(link)
    link.match?(FACEBOOK_REGEXP) ? Source.source_type.facebook : Source.source_type.rss
  end
end
