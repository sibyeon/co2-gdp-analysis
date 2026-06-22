knitr::opts_chunk$set(echo = TRUE, message = FALSE, warning = FALSE, fig.width = 7, fig.height = 4.5)
# install.packages(c("tidyverse","wbstats","janitor","skimr","broom","gt","GGally","readr","glue","yardstick"))
library(tidyverse)
library(wbstats)
library(janitor)
library(skimr)
library(broom)
library(gt)
library(GGally)
library(readr)
library(glue)
library(yardstick)
set.seed(301)

co2_code <- "EN.ATM.CO2E.PC"      # CO2 (metric tons per person)
gdp_code <- "NY.GDP.PCAP.KD"      # GDP per capita (constant 2015 USD)

fetch_worldbank <- function() {
  wb_data(
    indicator   = c(co2_pc = co2_code, gdp_pc = gdp_code),
    start_date  = 1990,
    end_date    = 2020,
    return_wide = TRUE
  ) %>%
    clean_names() %>%
    filter(!is.na(gdp_pc), !is.na(co2_pc)) %>%
    mutate(
      year    = as.integer(date),
      iso3c   = iso3c,
      country = country,
      region  = region,
      income  = income_level
    ) %>%
    select(iso3c, country, year, region, income, gdp_pc, co2_pc)
}

fetch_owid <- function() {
  owid <- read_csv("https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
                   show_col_types = FALSE) %>%
    clean_names() %>%
    filter(!is.na(population), !is.na(gdp), !is.na(co2_per_capita)) %>%
    transmute(
      iso3c   = iso_code,
      country = country,
      year    = year,
      co2_pc  = co2_per_capita,
      gdp_pc  = gdp / population
    ) %>%
    filter(year >= 1990, year <= 2020)

  meta <- wb_countries() %>%
    transmute(iso3c, region = region, income = income_level)

  owid %>% left_join(meta, by = "iso3c") %>% drop_na(region, income)
}

dat <- tryCatch(fetch_worldbank(), error = function(e) NULL)

source_label <- if (is.null(dat)) {
  dat <<- fetch_owid()
  "OWID (fallback) + WB metadata"
} else {
  "World Bank (wbstats)"
}

glue("Data source used: {source_label}; rows: {nrow(dat)}")

dat <- dat %>% clean_names()
dim(dat)
head(dat) %>% gt()

skim(dat %>% select(gdp_pc, co2_pc))

dat_model <- dat %>% mutate(log_gdp_pc = log1p(gdp_pc))

set.seed(301)
idx   <- sample(seq_len(nrow(dat_model)), size = 0.8*nrow(dat_model))
train <- dat_model[idx, ]
test  <- dat_model[-idx, ]

nrow(train); nrow(test)

train %>%
  ggplot(aes(x = gdp_pc, y = co2_pc)) +
  geom_point(alpha = 0.3, size = 1) +
  scale_x_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(x = "GDP per capita", y = "CO₂ per capita (t/person)",
       title = "CO₂ vs GDP per capita (Train, 1990–2020)") +
  geom_smooth(method = "loess", se = FALSE)

train %>%
  mutate(income = forcats::fct_relevel(income, "Low income","Lower middle income","Upper middle income","High income")) %>%
  ggplot(aes(gdp_pc, co2_pc, color = income)) +
  geom_point(alpha = 0.25, size = 0.8) +
  geom_smooth(se = FALSE) +
  scale_x_continuous(labels = scales::label_number(scale_cut = scales::cut_short_scale())) +
  labs(x = "GDP per capita", y = "CO₂ per capita", color = "Income group",
       title = "Relationship differs by income category") +
  facet_wrap(~ income, scales = "free")

m1 <- lm(co2_pc ~ log_gdp_pc, data = train)
summary(m1) %>% broom::tidy()

train %>%
  mutate(.fitted = predict(m1, newdata = train)) %>%
  ggplot(aes(log_gdp_pc, co2_pc)) +
  geom_point(alpha = 0.25) +
  geom_line(aes(y = .fitted), color = "steelblue") +
  labs(x = "log(GDP per capita + 1)", y = "CO₂ per capita",
       title = "Model 1: Fitted line on training data")

test %>%
  mutate(.fitted = predict(m1, newdata = test)) %>%
  ggplot(aes(log_gdp_pc, co2_pc)) +
  geom_point(alpha = 0.25) +
  geom_line(aes(y = .fitted), color = "steelblue") +
  labs(x = "log(GDP per capita + 1)", y = "CO₂ per capita",
       title = "Model 1: Predictions on test data")

pred_m1 <- augment(m1, newdata = test)
tibble(
  model = "Linear (log GDPpc)",
  rmse  = yardstick::rmse_vec(truth = test$co2_pc, estimate = pred_m1$.fitted),
  mae   = yardstick::mae_vec (truth = test$co2_pc, estimate = pred_m1$.fitted),
  r2    = yardstick::rsq_vec (truth = test$co2_pc, estimate = pred_m1$.fitted)
) %>% gt() %>% fmt_number(decimals = 3)

par(mfrow = c(1,2))
plot(m1, which = 1)  # residuals vs fitted
plot(m1, which = 2)  # QQ plot
par(mfrow = c(1,1))

m2 <- lm(co2_pc ~ log_gdp_pc + income + region, data = train)
summary(m2) %>% broom::tidy()

pred_m2 <- augment(m2, newdata = test)

bind_rows(
  tibble(model = "Linear (log GDPpc)",
         rmse  = yardstick::rmse_vec(truth = test$co2_pc, estimate = pred_m1$.fitted),
         mae   = yardstick::mae_vec (truth = test$co2_pc, estimate = pred_m1$.fitted),
         r2    = yardstick::rsq_vec (truth = test$co2_pc, estimate = pred_m1$.fitted)),
  tibble(model = "Multiple (+ income + region)",
         rmse  = yardstick::rmse_vec(truth = test$co2_pc, estimate = pred_m2$.fitted),
         mae   = yardstick::mae_vec (truth = test$co2_pc, estimate = pred_m2$.fitted),
         r2    = yardstick::rsq_vec (truth = test$co2_pc, estimate = pred_m2$.fitted))
) %>% gt() %>% fmt_number(decimals = 3)

train %>%
  mutate(.fitted = predict(m2, newdata = train)) %>%
  ggplot(aes(log_gdp_pc, co2_pc)) +
  geom_point(alpha = 0.25) +
  geom_line(aes(y = .fitted), color = "darkorange") +
  labs(x = "log(GDP per capita + 1)", y = "CO₂ per capita",
       title = "Model 2: Fitted values on training data")

test %>%
  mutate(.fitted = predict(m2, newdata = test)) %>%
  ggplot(aes(log_gdp_pc, co2_pc)) +
  geom_point(alpha = 0.25) +
  geom_line(aes(y = .fitted), color = "darkorange") +
  labs(x = "log(GDP per capita + 1)", y = "CO₂ per capita",
       title = "Model 2: Predictions on test data")

par(mfrow = c(1,2))
plot(m2, which = 1)
plot(m2, which = 2)
par(mfrow = c(1,1))

test %>%
  mutate(.pred_m1 = predict(m1, newdata = test),
         .pred_m2 = predict(m2, newdata = test)) %>%
  ggplot(aes(.pred_m1, .pred_m2)) +
  geom_point(alpha = 0.3) +
  geom_abline(linetype = 2) +
  labs(x = "Predicted CO₂ (Model 1)", y = "Predicted CO₂ (Model 2)",
       title = "Comparing Predictions: Simple vs Multiple Models")

sessionInfo()
