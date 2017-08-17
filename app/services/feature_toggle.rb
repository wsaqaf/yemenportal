class FeatureToggle
  def self.clustering_enabled?
    ENV["FT_CLUSTERING_ENABLED"] == "true"
  end

  def self.iframe_proxy_enabled?
    ENV["FT_IFRAME_PROXY_ENABLED"] == "true"
  end
end
