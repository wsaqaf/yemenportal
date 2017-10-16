class FeatureToggle
  def self.clustering_enabled?
    ENV["FT_CLUSTERING_ENABLED"] == "true"
  end
end
