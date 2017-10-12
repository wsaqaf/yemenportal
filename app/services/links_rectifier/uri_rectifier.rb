class LinksRectifier::UriRectifier
  def initialize(relative_url)
    @relative_uri = URI.parse(File.join("", relative_url))
  end

  def rectify(base_uri)
    if @relative_uri.host.blank?
      @relative_uri.scheme = base_uri.scheme
      @relative_uri.host = base_uri.host
    end
    @relative_uri.to_s
  end
end
